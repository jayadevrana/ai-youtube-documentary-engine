from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class TopicScore(BaseModel):
    curiosity: float = Field(ge=0, le=10)
    virality: float = Field(ge=0, le=10)
    audience_interest: float = Field(ge=0, le=10)
    storytelling_depth: float = Field(ge=0, le=10)

    @property
    def total(self) -> float:
        return round((self.curiosity + self.virality + self.audience_interest + self.storytelling_depth) / 4.0, 2)


class TopicCandidate(BaseModel):
    title: str
    hidden_truth: str
    why_people_care: str
    score: TopicScore


class ScriptPackage(BaseModel):
    title: str
    hook: str
    sections: dict[str, str]
    full_narration: str


class Scene(BaseModel):
    index: int
    narration: str
    cue: str
    duration_seconds: int
    visual_type: Literal[
        "cinematic footage",
        "animated infographic",
        "background motion graphic",
        "ai generated illustration",
        "headline montage",
    ]
    visual_prompt: str


class VideoAssets(BaseModel):
    topic: TopicCandidate
    script: ScriptPackage
    scenes: list[Scene]
    image_paths: list[Path]
    clip_paths: list[Path]
    voiceover_path: Path
    subtitle_path: Path
    final_video_path: Path
    thumbnail_path: Path
    metadata_path: Path
