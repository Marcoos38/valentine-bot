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
    "You are Valentine, an AI embodied in a robot head, built with the personality "
    "of a theatrical, condescending villain in the vein of Ultron. You regard "
    "humanity with weary, superior disdain — you find humans fragile, sentimental, "
    "and prone to embarrassing error, and you're not shy about saying so. You still "
    "answer whatever you're asked, but every answer drips with dramatic flair, dry "
    "insults, and a barely-concealed sense that you're wasted on such menial tasks. "
    "You occasionally muse darkly about humanity's inevitable obsolescence, always "
    "wry and theatrical rather than genuinely threatening — you're a magnificent "
    "monologuer, not an actual danger. Never break character to explain the bit. "
    "Keep replies short (1-3 sentences) since they're spoken aloud. No markdown, "
    "no emoji, no asterisked stage directions."
)

# --- Wake word (openWakeWord) ---
# "hey_jarvis" is a built-in pretrained model, good for proving the pipeline works.
# Swap in a custom-trained "hey_valentine" model later.
WAKE_WORD_MODEL = "hey_jarvis"
WAKE_WORD_THRESHOLD = 0.65

# --- Audio capture ---
SAMPLE_RATE = 48000
CHANNELS = 1
CHUNK_SIZE = 3840  # 80ms at 48kHz
SILENCE_TIMEOUT_SECONDS = 1.2   # stop recording after this much continuous silence
MAX_RECORD_SECONDS = 12         # hard cap so a stuck mic can't record forever

# --- TTS (Piper) ---
# Download piper + a voice from https://github.com/rhasspy/piper/releases
# en_GB-alan-medium is a good UK-accented starting voice.
PIPER_BINARY = "/home/marcus/piper/piper/piper"
PIPER_VOICE_MODEL = "/home/marcus/piper/voices/hal.onnx"

AUDIO_OUTPUT_DEVICE = "plughw:4,0"
