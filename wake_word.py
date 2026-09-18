"""
Continuous wake-word listening using openWakeWord.
"""
import numpy as np
from openwakeword.model import Model

import config
from audio_io import Microphone


class WakeWordListener:
    def __init__(self):
        self._model = Model(
            wakeword_models=[config.WAKE_WORD_MODEL],
            inference_framework="onnx",
        )

    def wait_for_wake_word(self, mic: Microphone, timeout_seconds=None) -> bool:
        downsample_factor = config.SAMPLE_RATE // 16000
        chunk_seconds = config.CHUNK_SIZE / config.SAMPLE_RATE
        elapsed = 0.0

        while True:
            chunk = mic.read_chunk()
            audio = np.frombuffer(chunk, dtype=np.int16)
            if downsample_factor > 1:
                audio = audio[::downsample_factor]
            predictions = self._model.predict(audio)

            for model_name, score in predictions.items():
                if score > config.WAKE_WORD_THRESHOLD:
                    print(f"[wake word] detected '{model_name}' (score={score:.2f})")
                    return True

            elapsed += chunk_seconds
            if timeout_seconds is not None and elapsed >= timeout_seconds:
                return False

    def warm_up(self, mic, seconds=1.0):
        """Feeds the model fresh audio without acting on it, to flush out
        stale internal buffer state after a pause (e.g. mid-conversation)."""
        downsample_factor = config.SAMPLE_RATE // 16000
        chunk_seconds = config.CHUNK_SIZE / config.SAMPLE_RATE
        chunks_needed = int(seconds / chunk_seconds) + 1

        for _ in range(chunks_needed):
            chunk = mic.read_chunk()
            audio = np.frombuffer(chunk, dtype=np.int16)
            if downsample_factor > 1:
                audio = audio[::downsample_factor]
            self._model.predict(audio)
