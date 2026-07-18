from __future__ import annotations

from pathlib import Path

from xmoney_mindset.models import Scene


class AnimationComposerAgent:
    """Prepares motion-support assets (subtitle timeline) for render pipeline."""

    @staticmethod
    def _ts(seconds: float) -> str:
        total_ms = int(seconds * 1000)
        hrs = total_ms // 3_600_000
        rem = total_ms % 3_600_000
        mins = rem // 60_000
        rem = rem % 60_000
        secs = rem // 1000
        ms = rem % 1000
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

    def build_subtitles(self, scenes: list[Scene], output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        cursor = 0.0

        for scene in scenes:
            start = cursor
            end = cursor + scene.duration_seconds
            lines.append(str(scene.index))
            lines.append(f"{self._ts(start)} --> {self._ts(end)}")
            lines.append(scene.narration)
            lines.append("")
            cursor = end

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path
