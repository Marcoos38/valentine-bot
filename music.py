"""
Background music playback via mpv, controllable through its IPC socket:
play, stop, skip, and duck/unduck volume while Valentine speaks over it.
"""
import json
import os
import random
import socket
import subprocess
import threading
import time

import config

SOCKET_PATH = "/tmp/valentine_mpv_socket"


class MusicPlayer:
    def __init__(self):
        self._process = None
        self._current_track = None
        self._lock = threading.Lock()

    def list_available_tracks(self):
        if not os.path.isdir(config.MUSIC_DIR):
            return []
        return [
            f for f in os.listdir(config.MUSIC_DIR)
            if f.lower().endswith((".mp3", ".wav", ".flac", ".ogg"))
        ]

    def _find_requested_track(self, user_text, tracks):
        lowered = user_text.lower()
        for track in tracks:
            if os.path.splitext(track)[0].lower() in lowered:
                return track
        return None

    def is_playing(self) -> bool:
        with self._lock:
            return self._process is not None and self._process.poll() is None

    def play(self, user_text: str = ""):
        tracks = self.list_available_tracks()
        if not tracks:
            return None
        track = self._find_requested_track(user_text, tracks) or random.choice(tracks)
        self._start_track(track)
        return track

    def skip(self):
        tracks = self.list_available_tracks()
        if not tracks:
            return None
        remaining = [t for t in tracks if t != self._current_track] or tracks
        track = random.choice(remaining)
        self._start_track(track)
        return track

    def _start_track(self, track):
        self.stop()
        path = os.path.join(config.MUSIC_DIR, track)
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        self._process = subprocess.Popen(
            [
                "mpv", "--no-video",
                f"--input-ipc-server={SOCKET_PATH}",
                f"--volume={config.MUSIC_NORMAL_VOLUME}",
                path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._current_track = track
        time.sleep(0.5)

    def stop(self):
        with self._lock:
            if self._process and self._process.poll() is None:
                self._send_command({"command": ["quit"]})
                try:
                    self._process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._process.kill()
            self._process = None
            self._current_track = None

    def duck(self):
        if self.is_playing():
            self._send_command({"command": ["set_property", "volume", config.MUSIC_DUCK_VOLUME]})

    def unduck(self):
        if self.is_playing():
            self._send_command({"command": ["set_property", "volume", config.MUSIC_NORMAL_VOLUME]})

    def _send_command(self, command_dict):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                sock.connect(SOCKET_PATH)
                sock.sendall((json.dumps(command_dict) + "\n").encode("utf-8"))
        except (FileNotFoundError, ConnectionRefusedError, socket.timeout, OSError):
            pass
