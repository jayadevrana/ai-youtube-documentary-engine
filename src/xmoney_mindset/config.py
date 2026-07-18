from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "xmoney_mindset"
    default_category: str = "finance / psychology / success"
    enable_real_generation: bool = False

    target_duration_minutes: int = 5
    scene_duration_seconds: int = 6
    fps: int = 30
    width: int = 1920
    height: int = 1080

    output_root: Path = Path("runs")
    cache_root: Path = Path(".cache")

    openai_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None

    openai_text_model: str = "gpt-4o-mini"
    openai_image_model: str = "gpt-image-1"
    openai_tts_model: str = "gpt-4o-mini-tts"
    openai_tts_voice: str = "alloy"

    local_tts_voice: str = "Daniel"
    background_music_path: Optional[str] = None

    @property
    def total_duration_seconds(self) -> int:
        return int(self.target_duration_minutes * 60)


settings = Settings()
