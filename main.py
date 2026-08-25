"""
Main loop: wait for wake word -> record -> transcribe -> think -> speak -> repeat.
"""
from audio_io import Microphone, record_until_silence
from wake_word import WakeWordListener
from stt import transcribe
from brain import Conversation
from tts import speak


def main():
    print("Starting up...")
    mic = Microphone()
    listener = WakeWordListener()
    conversation = Conversation()

    print("Ready. Waiting for wake word...")
    try:
        while True:
            listener.wait_for_wake_word(mic)

            print("Listening...")
            wav_bytes = record_until_silence(mic)

            print("Transcribing...")
            user_text = transcribe(wav_bytes)
            if not user_text:
                print("(heard nothing usable, going back to sleep)")
                continue
            print(f"You said: {user_text}")

            print("Thinking...")
            reply_text = conversation.respond(user_text)
            print(f"Reply: {reply_text}")

            speak(reply_text)
            print("Ready. Waiting for wake word...")

    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        mic.close()


if __name__ == "__main__":
    main()
