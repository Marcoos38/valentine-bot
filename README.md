# Valentine-bot prototype

Minimal wake-word → speech-to-text → Claude → text-to-speech loop, meant to
run on a Raspberry Pi. Get this working end-to-end first — no personality,
no expressions, no servos yet. Once the conversation loop feels responsive,
layer everything else on top.

## 1. System packages

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv portaudio19-dev alsa-utils
```

`portaudio19-dev` is required for PyAudio to build. `alsa-utils` gives you
`aplay`, which is used for playback.

## 2. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If `pyaudio` fails to install, it's almost always the missing
`portaudio19-dev` package above — re-run step 1 and try again.

## 3. Piper (text-to-speech)

Piper ships as a standalone binary, no pip install needed.

```bash
mkdir -p ~/piper/voices
cd ~/piper
wget https://github.com/rhasspy/piper/releases/latest/download/piper_arm64.tar.gz
tar -xzf piper_arm64.tar.gz
```

Then grab a voice model (this one's a UK male voice, decent starting point):

```bash
cd ~/piper/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json
```

Check the paths in `config.py` (`PIPER_BINARY`, `PIPER_VOICE_MODEL`) match
where you actually extracted things.

## 4. API keys

You need two:

- **Anthropic** (the "brain") — from console.anthropic.com
- **OpenAI** (used only for Whisper speech-to-text) — from platform.openai.com

Set them as environment variables rather than editing `config.py` directly:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

Add those two lines to `~/.bashrc` so they persist across reboots.

## 5. Run it

```bash
source venv/bin/activate
python3 main.py
```

Say "hey jarvis" (the placeholder wake word — see below), then speak your
question once you see `Listening...` in the terminal. It'll go quiet after
~1.2 seconds of silence and start processing.

## Known rough edges to expect

- **Wake word**: using openWakeWord's built-in "hey_jarvis" model for now
  since it works out of the box. Training a custom "hey valentine" model is
  a separate, later step — openWakeWord supports this but it needs a small
  training script and some synthetic/recorded samples.
- **Latency**: expect a few seconds end-to-end (record → Whisper → Claude →
  Piper → playback). This is the thing worth tuning once it's working, since
  latency is what kills the "alive" illusion.
- **Mic choice matters a lot** on a Pi — a cheap USB mic with poor gain will
  hurt both wake-word detection and transcription accuracy before anything
  else does.
- **VAD aggressiveness**: `webrtcvad.Vad(2)` in `audio_io.py` is a starting
  point. In a noisy room you may need `3` (more aggressive at rejecting
  non-speech); in a quiet room `1` might catch soft speech better.
