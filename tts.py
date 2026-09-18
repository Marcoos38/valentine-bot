"""
Text-to-speech using Piper, running locally on the Pi, with sox distortion
passes to move the voice away from its raw source.
"""
import subprocess
import tempfile
import os
import wave

import config
from audio_io import play_wav_file


def speak(text: str) -> float:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        raw_path = tmp.name
    processed_path = raw_path.replace(".wav", "_proc.wav")

    try:
        subprocess.run(
            [
                config.PIPER_BINARY,
                "--model", config.PIPER_VOICE_MODEL,
                "--output_file", raw_path,
            ],
            input=text.encode("utf-8"),
            check=True,
        )

        subprocess.run(
            [
                "sox", raw_path, processed_path,
                "gain", "-9",
                "pitch", "-150",
                "reverb", "20",
                "flanger", "0.5", "2", "25", "2", "0.5", "sine",
                "gain", "-n",
            ],
            check=True,
        )

        with wave.open(processed_path, "rb") as wf:
            duration = wf.getnframes() / wf.getframerate()

        play_wav_file(processed_path)
        return duration
    finally:
        for path in (raw_path, processed_path):
            if os.path.exists(path):
                os.remove(path)


def sing_daisy_bell() -> float:
    """Sings the public-domain 1892 song 'Daisy Bell', progressively slowing
    and lowering in pitch across each line for a 'dying' HAL-9000-style effect."""
    lines_and_speed = [
        ("Daisy, Daisy, give me your answer do.", 0.85),
        ("I'm half crazy, all for the love of you.", 0.72),
        ("It won't be a stylish marriage,", 0.6),
        ("I can't afford a carriage,", 0.5),
        ("But you'll look sweet, upon the seat,", 0.4),
        ("Of a bicycle built for two.", 0.3),
    ]

    segment_paths = []
    try:
        for line, speed in lines_and_speed:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                raw_path = tmp.name
            processed_path = raw_path.replace(".wav", "_proc.wav")

            subprocess.run(
                [
                    config.PIPER_BINARY,
                    "--model", config.PIPER_VOICE_MODEL,
                    "--output_file", raw_path,
                ],
                input=line.encode("utf-8"),
                check=True,
            )

            subprocess.run(
                [
                    "sox", raw_path, processed_path,
                    "gain", "-9",
                    "speed", str(speed),
                    "reverb", "35",
                    "gain", "-n",
                ],
                check=True,
            )
            segment_paths.append(processed_path)
            os.remove(raw_path)

        final_path = segment_paths[0].replace("_proc.wav", "_final.wav")
        subprocess.run(["sox"] + segment_paths + [final_path], check=True)

        with wave.open(final_path, "rb") as wf:
            duration = wf.getnframes() / wf.getframerate()

        play_wav_file(final_path)
        os.remove(final_path)
        return duration
    finally:
        for path in segment_paths:
            if os.path.exists(path):
                os.remove(path)


def speak_enraged(text: str) -> float:
    """Heavier pitch drop, real distortion, tremolo, and a layered sub-pitch
    'growl' voice mixed underneath for a doubled, menacing quality."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        raw_path = tmp.name
    main_path = raw_path.replace(".wav", "_main.wav")
    growl_path = raw_path.replace(".wav", "_growl.wav")
    mixed_path = raw_path.replace(".wav", "_mixed.wav")

    try:
        subprocess.run(
            [
                config.PIPER_BINARY,
                "--model", config.PIPER_VOICE_MODEL,
                "--output_file", raw_path,
            ],
            input=text.encode("utf-8"),
            check=True,
        )

        subprocess.run(
            [
                "sox", raw_path, main_path,
                "gain", "-9",
                "pitch", "-350",
                "overdrive", "12",
                "tremolo", "9", "45",
                "reverb", "25",
                "gain", "-n",
            ],
            check=True,
        )

        subprocess.run(
            [
                "sox", raw_path, growl_path,
                "gain", "-9",
                "pitch", "-1200",
                "gain", "-12",
            ],
            check=True,
        )

        subprocess.run(["sox", "-m", main_path, growl_path, mixed_path], check=True)

        with wave.open(mixed_path, "rb") as wf:
            duration = wf.getnframes() / wf.getframerate()

        play_wav_file(mixed_path)
        return duration
    finally:
        for path in (raw_path, main_path, growl_path, mixed_path):
            if os.path.exists(path):
                os.remove(path)
