from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from xmoney_mindset.config import Settings
from xmoney_mindset.models import Scene
from xmoney_mindset.services.openai_service import OpenAIService
from xmoney_mindset.utils.cache import cached_asset_path


class VisualGeneratorAgent:
    """Generates scene images from prompts using OpenAI or a local cinematic fallback."""

    def __init__(self, settings: Settings, openai_service: OpenAIService):
        self.settings = settings
        self.openai_service = openai_service

    def _wrap(self, text: str, max_chars: int = 64) -> str:
        words = text.split()
        lines: list[str] = []
        current: list[str] = []
        current_len = 0
        for word in words:
            if current_len + len(word) + (1 if current else 0) > max_chars:
                lines.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += len(word) + (1 if current_len else 0)
        if current:
            lines.append(" ".join(current))
        return "\n".join(lines)

    def _fallback_image(self, scene: Scene, output_path: Path) -> Path:
        w, h = self.settings.width, self.settings.height
        rnd = random.Random(scene.index)
        base = (rnd.randint(10, 35), rnd.randint(15, 45), rnd.randint(30, 70))
        accent = (rnd.randint(130, 220), rnd.randint(80, 170), rnd.randint(70, 140))

        image = Image.new("RGB", (w, h), base)
        draw = ImageDraw.Draw(image)

        for y in range(h):
            alpha = y / max(1, h - 1)
            r = int(base[0] * (1 - alpha) + accent[0] * alpha)
            g = int(base[1] * (1 - alpha) + accent[1] * alpha)
            b = int(base[2] * (1 - alpha) + accent[2] * alpha)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 58)
            body_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 34)
        except Exception:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()

        draw.rectangle([(90, 90), (w - 90, h - 90)], outline=(240, 240, 240), width=2)
        scene_header = f"SCENE {scene.index:03d} | {scene.visual_type.upper()}"
        draw.text((130, 130), scene_header, fill=(255, 255, 255), font=title_font)

        narration = self._wrap(scene.narration, max_chars=68)
        draw.text((130, 260), narration, fill=(235, 235, 235), font=body_font, spacing=8)

        cue = f"Cue: {scene.cue}"
        draw.text((130, h - 180), cue, fill=(250, 240, 220), font=body_font)
        draw.text((130, h - 130), "xmoney_mindset test render", fill=(230, 230, 230), font=body_font)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
        return output_path

    def generate(self, scenes: list[Scene], output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[Path] = []

        for scene in scenes:
            desired_path = output_dir / f"scene_{scene.index:03d}.png"
            cache_path = cached_asset_path(self.settings.cache_root, "images", scene.visual_prompt, "png")
            if cache_path.exists() and not desired_path.exists():
                desired_path.write_bytes(cache_path.read_bytes())
                results.append(desired_path)
                continue
            if desired_path.exists():
                results.append(desired_path)
                continue

            created_path = None
            if self.settings.enable_real_generation and self.openai_service.available:
                try:
                    created_path = self.openai_service.generate_image(scene.visual_prompt, desired_path)
                except Exception:
                    created_path = None

            if created_path is None:
                created_path = self._fallback_image(scene, desired_path)

            if created_path.exists():
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                if not cache_path.exists():
                    cache_path.write_bytes(created_path.read_bytes())

            results.append(created_path)

        return results
