from __future__ import annotations

from pathlib import Path

from xmoney_mindset.models import Scene, ScriptPackage, TopicCandidate
from xmoney_mindset.services.openai_service import OpenAIService
from xmoney_mindset.utils.io import dump_json


class YouTubeOptimizerAgent:
    """Builds title, description, tags, and thumbnail concept for publishing."""

    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service

    def _fallback(
        self,
        topic: TopicCandidate,
        script: ScriptPackage,
        scenes: list[Scene],
    ) -> dict:
        title = topic.title
        description = (
            f"{script.hook}\n\n"
            "In this documentary, we investigate the belief systems around money, "
            "success culture, and modern leverage.\n\n"
            "Chapters:\n"
            "00:00 Hook\n"
            "01:00 The Illusion\n"
            "03:00 Investigation\n"
            "05:00 Psychology\n"
            "07:00 Hidden Truth\n"
            "09:00 Resolution\n"
        )
        tags = [
            "finance psychology",
            "wealth mindset",
            "success documentary",
            "money myths",
            "self improvement",
            "investigative documentary",
            "xmoney mindset",
        ]
        thumbnail = {
            "headline": "THE MONEY ILLUSION",
            "subtext": "What They Never Explain",
            "visual": "Split frame: luxury facade vs exhausted worker; cinematic contrast, golden and dark tones",
        }
        return {
            "title": title,
            "description": description,
            "tags": tags,
            "thumbnail_concept": thumbnail,
            "estimated_scene_count": len(scenes),
        }

    def generate(
        self,
        topic: TopicCandidate,
        script: ScriptPackage,
        scenes: list[Scene],
        output_path: Path,
    ) -> Path:
        payload = self._fallback(topic, script, scenes)

        if self.openai_service.available:
            try:
                system = "You are a YouTube SEO strategist for cinematic finance documentaries."
                user = (
                    f"Topic: {topic.title}\n"
                    f"Hook: {script.hook}\n"
                    "Return plain text with sections TITLE, DESCRIPTION, TAGS (comma-separated), THUMBNAIL."
                )
                text = self.openai_service.generate_text(system, user)
                if text:
                    payload["llm_variant"] = text
            except Exception:
                pass

        dump_json(output_path, payload)
        return output_path
