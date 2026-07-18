from __future__ import annotations

import subprocess
from pathlib import Path


class MediaService:
    @staticmethod
    def run(command: list[str]) -> None:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                "Command failed: " + " ".join(command) + "\n" + result.stderr.strip()
            )

    @staticmethod
    def ffprobe_duration(path: Path) -> float:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return 0.0
        try:
            return float(result.stdout.strip())
        except ValueError:
            return 0.0
