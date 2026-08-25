"""
Continuous wake-word listening using openWakeWord.
"""
import numpy as np
from openwakeword.model import Model

import config
from audio_io import Microphone


class WakeWordListener:
    def __init__(self):
        self._model = Model(wakeword_models=[config.WAKE_WORD_MODEL])

    def wait_for_wake_word(self, mic: Microphone):
        """Blocks until the configured wake word is detected."""
        while True:
            chunk = mic.read_chunk()
            audio = np.frombuffer(chunk, dtype=np.int16)
            predictions = self._model.predict(audio)

            for model_name, score in predictions.items():
                if score > config.WAKE_WORD_THRESHOLD:
                    print(f"[wake word] detected '{model_name}' (score={score:.2f})")
                    return
