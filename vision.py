"""
Captures a single frame from the eye camera and returns it as base64,
ready to send to Claude's vision capability.
"""
import subprocess
import tempfile
import os
import base64

import config


def capture_frame_base64() -> str:
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        path = tmp.name

    try:
        subprocess.run(
            [
                "fswebcam",
                "-d", config.CAMERA_DEVICE,
                "--skip", str(config.VISION_CAPTURE_SKIP_FRAMES),
                "-r", "640x480",
                "--no-banner",
                path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    finally:
        if os.path.exists(path):
            os.remove(path)
