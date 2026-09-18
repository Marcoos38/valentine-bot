"""
Main loop: wait for wake word (or idle) -> record -> transcribe -> think -> speak -> repeat.
"""
import random
import time

import config
from audio_io import Microphone, record_until_silence
from wake_word import WakeWordListener
from stt import transcribe
from brain import Conversation
from tts import speak, sing_daisy_bell, speak_enraged
from memory import summarize_and_store, load_memory_digest
from idle import pick_idle_comment
from vision import capture_frame_base64
from music import MusicPlayer


def _check_easter_eggs(user_text: str):
    lowered = user_text.lower()
    for egg in config.EASTER_EGGS:
        if any(trigger in lowered for trigger in egg["triggers"]):
            return egg["response"]
    return None


def speak_ducked(music_player, text, mode="normal"):
    music_player.duck()
    if mode == "sing":
        duration = sing_daisy_bell()
    elif mode == "enraged":
        duration = speak_enraged(text)
    else:
        duration = speak(text)
    music_player.unduck()
    return duration


def run_conversation_turn(mic, conversation, wav_bytes, music_player) -> bool:
    if wav_bytes is None:
        print("(no speech heard, going back to sleep)")
        mic.flush()
        return False

    print("Transcribing...")
    try:
        user_text = transcribe(wav_bytes)
    except Exception as e:
        print(f"(transcription failed: {e}, going back to sleep)")
        mic.flush()
        return False
    if not user_text:
        print("(heard nothing usable, going back to sleep)")
        mic.flush()
        return False
    print(f"You said: {user_text}")
    lowered = user_text.lower()

    if any(phrase in lowered for phrase in config.STOP_MUSIC_TRIGGERS):
        if music_player.is_playing():
            music_player.stop()
            print("(music stopped)")
        else:
            duration = speak_ducked(music_player, "There's nothing playing, genius.")
            mic.flush()
            time.sleep(max(0.5, duration * 0.15))
        return True

    if any(phrase in lowered for phrase in config.SKIP_MUSIC_TRIGGERS):
        if music_player.is_playing():
            track = music_player.skip()
            print(f"(skipped to {track})")
        else:
            duration = speak_ducked(music_player, "Skip to what? Nothing's playing.")
            mic.flush()
            time.sleep(max(0.5, duration * 0.15))
        return True

    if any(phrase in lowered for phrase in config.MUSIC_TRIGGERS):
        complaint = random.choice(config.MUSIC_COMPLAINTS)
        print(f"Valentine: {complaint}")
        duration = speak_ducked(music_player, complaint)
        mic.flush()
        time.sleep(max(0.5, duration * 0.15))

        track = music_player.play(user_text)
        if track:
            print(f"(playing {track})")
        else:
            no_music_line = "I don't even have anything to play. How embarrassing for both of us."
            duration = speak_ducked(music_player, no_music_line)
            mic.flush()
            time.sleep(max(0.5, duration * 0.15))
        return True

    egg_response = _check_easter_eggs(user_text)
    if egg_response:
        print(f"Reply (easter egg): {egg_response}")
        conversation.get_history().append({"role": "user", "content": user_text})
        conversation.get_history().append({"role": "assistant", "content": egg_response})
        mode = "enraged" if "hate" in egg_response.lower() else "normal"
        duration = speak_ducked(music_player, egg_response, mode=mode)
        mic.flush()
        time.sleep(max(0.5, duration * 0.15))
        return True

    if any(phrase in lowered for phrase in config.SING_TRIGGERS):
        print("Reply (easter egg): [sings Daisy Bell]")
        conversation.get_history().append({"role": "user", "content": user_text})
        conversation.get_history().append({"role": "assistant", "content": "[sang Daisy Bell]"})
        duration = speak_ducked(music_player, "", mode="sing")
        mic.flush()
        time.sleep(max(0.5, duration * 0.15))
        return True

    print("Thinking...")
    reply_text = conversation.respond(user_text, capture_frame_fn=capture_frame_base64)
    print(f"Reply: {reply_text}")

    if not reply_text.strip():
        print("(empty reply, skipping speech)")
        return True

    duration = speak_ducked(music_player, reply_text)
    mic.flush()
    time.sleep(max(0.5, duration * 0.15))
    return True


def main():
    print("Starting up...")
    mic = Microphone()
    listener = WakeWordListener()
    music_player = MusicPlayer()

    mood = random.choice(config.MOODS)
    print(f"(mood for this session: {mood['name']})")
    conversation = Conversation(mood_modifier=mood["prompt"])

    ignored_idle_count = 0

    boot_line = random.choice(config.BOOT_UP_LINES)
    print(f"Valentine: {boot_line}")
    duration = speak_ducked(music_player, boot_line)
    mic.flush()
    time.sleep(max(0.5, duration * 0.15))

    print("Ready. Waiting for wake word...")
    try:
        while True:
            idle_timeout = random.uniform(
                config.IDLE_COMMENT_MIN_SECONDS, config.IDLE_COMMENT_MAX_SECONDS
            )
            woke_normally = listener.wait_for_wake_word(mic, timeout_seconds=idle_timeout)

            if woke_normally:
                ignored_idle_count = 0
                ack = random.choice(config.WAKE_ACKNOWLEDGMENTS)
                print(f"Valentine: {ack}")
                duration = speak_ducked(music_player, ack)
                mic.flush()
                time.sleep(max(0.5, duration * 0.15))

                print("Listening...")
                wav_bytes = record_until_silence(mic)
            else:
                memory_digest = load_memory_digest()
                comment = pick_idle_comment(memory_digest, mood["name"], ignored_idle_count)
                print(f"Valentine (idle): {comment}")
                duration = speak_ducked(music_player, comment)
                mic.flush()
                time.sleep(max(0.5, duration * 0.15))

                print("Listening for a response...")
                wav_bytes = record_until_silence(
                    mic, pre_speech_timeout_seconds=config.IDLE_RESPONSE_WINDOW_SECONDS
                )

                if wav_bytes is None:
                    ignored_idle_count += 1
                else:
                    ignored_idle_count = 0

            in_conversation = run_conversation_turn(mic, conversation, wav_bytes, music_player)

            while in_conversation:
                print("Listening for follow-up...")
                wav_bytes = record_until_silence(
                    mic, pre_speech_timeout_seconds=config.CONVERSATION_TIMEOUT_SECONDS
                )
                in_conversation = run_conversation_turn(mic, conversation, wav_bytes, music_player)

            if conversation.get_history():
                summarize_and_store(conversation.get_history())
                conversation.reset()

            listener.warm_up(mic)
            print("Ready. Waiting for wake word...")

    except KeyboardInterrupt:
        print("\nShutting down.")
        music_player.stop()
        if conversation.get_history():
            print("Saving memory before exit...")
            try:
                summarize_and_store(conversation.get_history())
            except Exception as e:
                print(f"(failed to save memory: {e})")
    finally:
        mic.close()


if __name__ == "__main__":
    main()
