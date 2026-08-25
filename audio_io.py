"""
Microphone capture, silence-based recording cutoff, and playback.
"""
import io
import wave
import subprocess

import numpy as np
import pyaudio
import webrtcvad

import config


class Microphone:
    """Wraps a PyAudio input stream, yielding raw int16 chunks."""

    def __init__(self):
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.CHUNK_SIZE,
        )

    def read_chunk(self) -> bytes:
        return self._stream.read(config.CHUNK_SIZE, exception_on_overflow=False)

    def close(self):
        self._stream.stop_stream()
        self._stream.close()
        self._pa.terminate()


def record_until_silence(mic: Microphone) -> bytes:
    """
    Records audio from the mic starting immediately, and stops once
    SILENCE_TIMEOUT_SECONDS of continuous silence is detected (or the
    MAX_RECORD_SECONDS cap is hit). Returns WAV bytes.
    """
    vad = webrtcvad.Vad(2)  # aggressiveness 0-3; 2 is a reasonable middle ground
    frames = []

    silence_chunks_needed = int(
        config.SILENCE_TIMEOUT_SECONDS * config.SAMPLE_RATE / config.CHUNK_SIZE
    )
    max_chunks = int(
        config.MAX_RECORD_SECONDS * config.SAMPLE_RATE / config.CHUNK_SIZE
    )

    silence_run = 0
    heard_speech = False

    for _ in range(max_chunks):
        chunk = mic.read_chunk()
        frames.append(chunk)

        # webrtcvad wants 10/20/30ms frames; our 80ms chunk is split into 20ms sub-frames
        is_speech = _chunk_has_speech(vad, chunk)

        if is_speech:
            heard_speech = True
            silence_run = 0
        elif heard_speech:
            silence_run += 1
            if silence_run >= silence_chunks_needed:
                break

    return _frames_to_wav(frames)


def _chunk_has_speech(vad: webrtcvad.Vad, chunk: bytes) -> bool:
    frame_bytes = int(config.SAMPLE_RATE * 0.02) * 2  # 20ms, 16-bit samples
    for i in range(0, len(chunk) - frame_bytes + 1, frame_bytes):
        frame = chunk[i:i + frame_bytes]
        if vad.is_speech(frame, config.SAMPLE_RATE):
            return True
    return False


def _frames_to_wav(frames) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(config.CHANNELS)
        wf.setsampwidth(2)  # int16
        wf.setframerate(config.SAMPLE_RATE)
        wf.writeframes(b"".join(frames))
    return buf.getvalue()


def play_wav_file(path: str):
    """Plays a WAV file using aplay (standard on Raspberry Pi OS)."""
    subprocess.run(["aplay", "-q", path], check=False)
