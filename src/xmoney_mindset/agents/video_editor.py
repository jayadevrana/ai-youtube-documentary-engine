from __future__ import annotations

from pathlib import Path

from xmoney_mindset.config import Settings
from xmoney_mindset.services.media_service import MediaService


class VideoEditorAgent:
    """Combines clips, voiceover, and optional background music into final MP4."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def _concat_clips(self, clip_paths: list[Path], output_path: Path) -> Path:
        list_file = output_path.parent / "concat.txt"
        lines = [f"file '{clip.resolve()}'" for clip in clip_paths]
        list_file.write_text("\n".join(lines), encoding="utf-8")

        MediaService.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c",
                "copy",
                str(output_path),
            ]
        )
        return output_path

    def assemble(
        self,
        clip_paths: list[Path],
        voiceover_path: Path,
        subtitle_path: Path,
        output_dir: Path,
    ) -> tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        stitched_video = output_dir / "stitched_video.mp4"
        final_video = output_dir / "final_video.mp4"
        thumbnail = output_dir / "thumbnail.jpg"

        self._concat_clips(clip_paths, stitched_video)

        bg_music = self.settings.background_music_path
        if bg_music and Path(bg_music).exists():
            command = [
                "ffmpeg",
                "-y",
                "-i",
                str(stitched_video),
                "-i",
                str(voiceover_path),
                "-stream_loop",
                "-1",
                "-i",
                str(Path(bg_music)),
                "-filter_complex",
                "[1:a]volume=1.0[voice];[2:a]volume=0.10[bg];[voice][bg]amix=inputs=2:duration=shortest[aout]",
                "-map",
                "0:v:0",
                "-map",
                "[aout]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(final_video),
            ]
        else:
            command = [
                "ffmpeg",
                "-y",
                "-i",
                str(stitched_video),
                "-i",
                str(voiceover_path),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(final_video),
            ]

        MediaService.run(command)

        # Optional subtitle sidecar preserved for upload/editor use.
        if subtitle_path.exists():
            copied_srt = output_dir / "captions.srt"
            if copied_srt != subtitle_path:
                copied_srt.write_text(subtitle_path.read_text(encoding="utf-8"), encoding="utf-8")

        MediaService.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(final_video),
                "-ss",
                "00:00:03",
                "-vframes",
                "1",
                str(thumbnail),
            ]
        )

        return final_video, thumbnail
