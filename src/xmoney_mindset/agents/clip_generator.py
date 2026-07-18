from __future__ import annotations

from pathlib import Path

from xmoney_mindset.config import Settings
from xmoney_mindset.models import Scene
from xmoney_mindset.services.media_service import MediaService


class ClipGeneratorAgent:
    """Turns scene images into short cinematic clips with pan/zoom motion."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def generate(self, scenes: list[Scene], image_paths: list[Path], output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[Path] = []

        for scene, image_path in zip(scenes, image_paths):
            clip_path = output_dir / f"clip_{scene.index:03d}.mp4"
            if clip_path.exists():
                results.append(clip_path)
                continue

            duration = scene.duration_seconds
            fps = self.settings.fps
            frames = duration * fps
            fade_out_start = max(0.1, duration - 0.45)

            vf = (
                f"scale={self.settings.width}:{self.settings.height},"
                f"zoompan=z='min(zoom+0.0007,1.12)':d={frames}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"s={self.settings.width}x{self.settings.height},"
                f"fps={fps},"
                f"fade=t=in:st=0:d=0.4,"
                f"fade=t=out:st={fade_out_start}:d=0.4"
            )

            command = [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(image_path),
                "-vf",
                vf,
                "-t",
                str(duration),
                "-pix_fmt",
                "yuv420p",
                "-c:v",
                "libx264",
                str(clip_path),
            ]
            MediaService.run(command)
            results.append(clip_path)

        return results
