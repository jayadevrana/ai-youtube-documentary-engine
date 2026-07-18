from __future__ import annotations

import subprocess
from pathlib import Path

from xmoney_mindset.config import Settings
from xmoney_mindset.services.media_service import MediaService
from xmoney_mindset.services.openai_service import OpenAIService


class VoiceoverGeneratorAgent:
    """Generates narration audio using OpenAI TTS or local fallback."""

    def __init__(self, settings: Settings, openai_service: OpenAIService):
        self.settings = settings
        self.openai_service = openai_service

    def _local_tts(self, narration_text: str, output_path: Path, temp_dir: Path) -> Path | None:
        temp_dir.mkdir(parents=True, exist_ok=True)
        script_path = temp_dir / "narration.txt"
        aiff_path = temp_dir / "narration.aiff"
        script_path.write_text(narration_text, encoding="utf-8")

        say_cmd = [
            "say",
            "-v",
            self.settings.local_tts_voice,
            "-r",
            "165",
            "-f",
            str(script_path),
            "-o",
            str(aiff_path),
        ]
        proc = subprocess.run(say_cmd, capture_output=True, text=True)
        if proc.returncode != 0 or not aiff_path.exists():
            return None

        MediaService.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(aiff_path),
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                str(output_path),
            ]
        )
        return output_path if output_path.exists() else None

    def _silent_fallback(self, duration_seconds: int, output_path: Path) -> Path:
        MediaService.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=48000:cl=stereo",
                "-t",
                str(duration_seconds),
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                str(output_path),
            ]
        )
        return output_path

    def generate(self, narration_text: str, duration_seconds: int, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "voiceover.m4a"
        if output_path.exists():
            return output_path

        if self.settings.enable_real_generation and self.openai_service.available:
            try:
                return self.openai_service.generate_tts(narration_text, output_path)
            except Exception:
                pass

        local = self._local_tts(narration_text, output_path, output_dir / "_tmp")
        if local is not None:
            return local

        return self._silent_fallback(duration_seconds, output_path)
