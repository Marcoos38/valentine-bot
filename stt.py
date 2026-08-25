"""
Speech-to-text using OpenAI's hosted Whisper API.

Using the API instead of running Whisper locally because Whisper (even the
small models) is slow on a Pi's CPU. This trades a small per-call cost and
a network round trip for much lower latency and zero local compute load.
"""
import requests

import config

WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"


def transcribe(wav_bytes: bytes) -> str:
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    response = requests.post(
        WHISPER_URL,
        headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
        files={"file": ("audio.wav", wav_bytes, "audio/wav")},
        data={"model": "whisper-1"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["text"].strip()
