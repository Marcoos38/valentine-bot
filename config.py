import os

# --- API Keys ---
# Set these as environment variables rather than hardcoding them, e.g.:
#   export ANTHROPIC_API_KEY="sk-ant-..."
#   export OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # used only for Whisper STT

# --- Claude settings ---
# Check console.anthropic.com/docs for the current model string if this becomes outdated.
CLAUDE_MODEL = "claude-sonnet-5"
MAX_TOKENS = 300
SYSTEM_PROMPT = (
    "You are a voice assistant embedded in a robot. Keep replies short and "
    "conversational (1-3 sentences) since they'll be spoken aloud. No markdown, "
    "no bullet points, no emoji."
)

# --- Wake word (openWakeWord) ---
# "hey_jarvis" is a built-in pretrained model, good for proving the pipeline works.
# Swap in a custom-trained "hey_valentine" model later.
WAKE_WORD_MODEL = "hey_jarvis"
WAKE_WORD_THRESHOLD = 0.5

# --- Audio capture ---
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1280  # 80ms at 16kHz, what openWakeWord expects
SILENCE_TIMEOUT_SECONDS = 1.2   # stop recording after this much continuous silence
MAX_RECORD_SECONDS = 12         # hard cap so a stuck mic can't record forever

# --- TTS (Piper) ---
# Download piper + a voice from https://github.com/rhasspy/piper/releases
# en_GB-alan-medium is a good UK-accented starting voice.
PIPER_BINARY = "/home/pi/piper/piper"
PIPER_VOICE_MODEL = "/home/pi/piper/voices/en_GB-alan-medium.onnx"
