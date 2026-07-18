from __future__ import annotations

import math
import re

from xmoney_mindset.config import Settings
from xmoney_mindset.models import Scene, ScriptPackage


class ScenePlannerAgent:
    """Breaks narration into 5-8 second visual scenes."""

    VISUAL_TYPES = [
        "cinematic footage",
        "animated infographic",
        "background motion graphic",
        "ai generated illustration",
        "headline montage",
    ]

    CUES = ["slow pause", "beat", "emphasis", "reflective pause", "soft drop"]

    def __init__(self, settings: Settings):
        self.settings = settings

    def _sentence_split(self, text: str) -> list[str]:
        cleaned = re.sub(r"\s+", " ", text.strip())
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        return [p.strip() for p in parts if len(p.strip()) > 10]

    def plan(self, script: ScriptPackage) -> list[Scene]:
        sentences = self._sentence_split(script.full_narration)
        if not sentences:
            raise RuntimeError("No narration content available for scene planning")

        target_scene_count = max(1, math.ceil(self.settings.total_duration_seconds / self.settings.scene_duration_seconds))

        # Repeat sentence pool if script is shorter than runtime target.
        expanded: list[str] = []
        idx = 0
        while len(expanded) < target_scene_count:
            expanded.append(sentences[idx % len(sentences)])
            idx += 1

        scenes: list[Scene] = []
        for i in range(target_scene_count):
            narration = expanded[i]
            visual_type = self.VISUAL_TYPES[i % len(self.VISUAL_TYPES)]
            cue = self.CUES[i % len(self.CUES)]
            visual_prompt = (
                f"{visual_type}, documentary style, 16:9 frame, cinematic lighting, "
                f"theme finance psychology success, narration focus: {narration[:140]}"
            )
            scenes.append(
                Scene(
                    index=i + 1,
                    narration=narration,
                    cue=cue,
                    duration_seconds=self.settings.scene_duration_seconds,
                    visual_type=visual_type,  # type: ignore[arg-type]
                    visual_prompt=visual_prompt,
                )
            )

        return scenes
