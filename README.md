# Valentine-bot - full backup

This is the complete, current state of the Valentine conversational AI project: wake word, conversation loop, personality, long-term
memory, idle behavior, vision (camera), and background music with ducking.

## Files

- `config.py` - all settings: personality prompt, moods, triggers, audio config
- `audio_io.py` - microphone capture and playback
- `wake_word.py` - openWakeWord wake-word detection
- `stt.py` - Whisper speech-to-text
- `brain.py` - Claude conversation logic, including the `look` vision tool
- `tts.py` - Piper text-to-speech with sox voice distortion effects
- `memory.py` - long-term memory across power cycles
- `idle.py` - unprompted idle comments (mood-aware, vision-aware, escalating)
- `vision.py` - camera frame capture
- `music.py` - background music player with ducking, skip, stop
- `main.py` - the main loop tying everything together
- `requirements.txt` - Python dependencies

## Not included here (separate from code)

- `~/.asoundrc` or `/etc/asound.conf` - the ALSA audio routing config that lets
  music and speech play simultaneously. This needs setting up separately on
  the Pi (see prior conversation for the exact content).
- `~/valentine-bot/music/` - your actual mp3 files, not code, upload separately.
- `~/piper/` - the Piper binary and voice model files, downloaded separately
  per the setup steps (not part of this repo).
- `memory.json` - gets created automatically once a real conversation happens;
  don't need to create this yourself.

## Setup on a fresh Pi

1. Enable I2C if using servos (raspi-config)
2. Install system packages: `python3-pip python3-venv portaudio19-dev alsa-utils git sox mpv fswebcam i2c-tools`
3. Set up venv, `pip install -r requirements.txt`, then `pip install "setuptools<81"`
4. Install Piper separately (binary + voice model)
5. Set `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` as environment variables
6. Adjust the hardcoded paths in `config.py` (`PIPER_BINARY`, `PIPER_VOICE_MODEL`)
   to match your actual username/paths
7. Set up `/etc/asound.conf` for audio device routing
8. Run `python3 main.py`
