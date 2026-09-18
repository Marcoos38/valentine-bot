"""
Microphone capture, silence-based recording cutoff, and playback.
"""
import io
import wave
import subprocess

import webrtcvad

import config


class Microphone:
    def __init__(self):
        import pyaudio
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

    def flush(self):
        self._stream.stop_stream()
        self._stream.start_stream()

    def close(self):
        self._stream.stop_stream()
        self._stream.close()
        self._pa.terminate()


def record_until_silence(mic: Microphone, pre_speech_timeout_seconds=None):
    vad = webrtcvad.Vad(2)
    frames = []

    silence_chunks_needed = int(
        config.SILENCE_TIMEOUT_SECONDS * config.SAMPLE_RATE / config.CHUNK_SIZE
    )
    max_chunks = int(
        config.MAX_RECORD_SECONDS * config.SAMPLE_RATE / config.CHUNK_SIZE
    )

    pre_speech_seconds = (
        pre_speech_timeout_seconds
        if pre_speech_timeout_seconds is not None
        else config.MAX_RECORD_SECONDS
    )
    pre_speech_max_chunks = int(pre_speech_seconds * config.SAMPLE_RATE / config.CHUNK_SIZE)

    silence_run = 0
    speech_run = 0
    heard_speech = False
    MIN_CONSECUTIVE_SPEECH_CHUNKS = 3

    chunk_count = 0
    for _ in range(max_chunks):
        chunk = mic.read_chunk()
        frames.append(chunk)
        chunk_count += 1

        is_speech = _chunk_has_speech(vad, chunk)

        if is_speech:
            speech_run += 1
            silence_run = 0
            if speech_run >= MIN_CONSECUTIVE_SPEECH_CHUNKS:
                heard_speech = True
        else:
            speech_run = 0
            if heard_speech:
                silence_run += 1
                if silence_run >= silence_chunks_needed:
                    break

        if not heard_speech and chunk_count >= pre_speech_max_chunks:
            return None

    if not heard_speech:
        return None

    return _frames_to_wav(frames)


def _chunk_has_speech(vad: webrtcvad.Vad, chunk: bytes) -> bool:
    frame_bytes = int(config.SAMPLE_RATE * 0.02) * 2
    for i in range(0, len(chunk) - frame_bytes + 1, frame_bytes):
        frame = chunk[i:i + frame_bytes]
        if vad.is_speech(frame, config.SAMPLE_RATE):
            return True
    return False


def _frames_to_wav(frames) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(config.CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(config.SAMPLE_RATE)
        wf.writeframes(b"".join(frames))
    return buf.getvalue()


def play_wav_file(path: str):
    subprocess.run(["aplay", "-q", "-D", config.AUDIO_OUTPUT_DEVICE, path], check=False)
