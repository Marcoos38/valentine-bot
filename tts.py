"""
Text-to-speech using Piper, running locally on the Pi.
"""
import subprocess
import tempfile
import os

import config
from audio_io import play_wav_file


def speak(text: str):
    """Synthesizes text to a temp WAV file with Piper, then plays it."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        out_path = tmp.name

    try:
        subprocess.run(
            [
                config.PIPER_BINARY,
                "--model", config.PIPER_VOICE_MODEL,
                "--output_file", out_path,
            ],
            input=text.encode("utf-8"),
            check=True,
        )
        play_wav_file(out_path)
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)
