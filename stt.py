"""
Speech-to-text using OpenAI's hosted Whisper API.

Using the API instead of running Whisper locally because Whisper (even the
small models) is slow on a Pi's CPU. This trades a small per-call cost and
a network round trip for much lower latency and zero local compute load.
"""
import re
import requests

import config

WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"
_KNOWN_HALLUCINATIONS = {
    "thank you", "thank you.", "thanks.", "thanks for watching",
    "thanks for watching.", "thanks for watching!",
    "thank you for watching", "thank you for watching!",
    "please subscribe.", "you", ".", "..", ". .",
}

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
    if not response.ok:
        print(f"Whisper API error {response.status_code}: {response.text}")
    response.raise_for_status()
    text = response.json()["text"].strip()

    normalized = text.lower().strip(" .!")
    if normalized in _KNOWN_HALLUCINATIONS or "thank you" in normalized or "thanks for watching" in normalized:
        return ""

    # Catch anything that's just punctuation/whitespace with no real words in it
    if not re.search(r"[a-zA-Z0-9]", text):
        return ""

    return text
