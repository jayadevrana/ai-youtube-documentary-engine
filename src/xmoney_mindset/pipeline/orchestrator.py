from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from xmoney_mindset.agents.animation_composer import AnimationComposerAgent
from xmoney_mindset.agents.clip_generator import ClipGeneratorAgent
from xmoney_mindset.agents.scene_planner import ScenePlannerAgent
from xmoney_mindset.agents.script_writer import ScriptWriterAgent
from xmoney_mindset.agents.topic_research import TopicResearchAgent
from xmoney_mindset.agents.video_editor import VideoEditorAgent
from xmoney_mindset.agents.visual_generator import VisualGeneratorAgent
from xmoney_mindset.agents.voiceover_generator import VoiceoverGeneratorAgent
from xmoney_mindset.agents.youtube_optimizer import YouTubeOptimizerAgent
from xmoney_mindset.config import Settings
from xmoney_mindset.models import TopicCandidate, VideoAssets
from xmoney_mindset.services.openai_service import OpenAIService
from xmoney_mindset.utils.io import dump_json, ensure_dir


@dataclass
class PipelineResult:
    run_dir: Path
    assets: VideoAssets


class XMoneyPipeline:
    """End-to-end autonomous generation pipeline for one documentary video."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.openai_service = OpenAIService(settings)

        self.topic_research = TopicResearchAgent(self.openai_service)
        self.script_writer = ScriptWriterAgent(settings, self.openai_service)
        self.scene_planner = ScenePlannerAgent(settings)
        self.visual_generator = VisualGeneratorAgent(settings, self.openai_service)
        self.clip_generator = ClipGeneratorAgent(settings)
        self.voiceover_generator = VoiceoverGeneratorAgent(settings, self.openai_service)
        self.animation_composer = AnimationComposerAgent()
        self.video_editor = VideoEditorAgent(settings)
        self.youtube_optimizer = YouTubeOptimizerAgent(self.openai_service)

    def _make_run_dir(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return ensure_dir(self.settings.output_root / timestamp)

    def _build_manifest(
        self,
        run_dir: Path,
        topic: TopicCandidate,
        script,
        scenes,
        image_paths,
        clip_paths,
        voiceover_path,
        subtitle_path,
        final_video_path,
        thumbnail_path,
        metadata_path,
    ) -> VideoAssets:
        manifest = VideoAssets(
            topic=topic,
            script=script,
            scenes=scenes,
            image_paths=image_paths,
            clip_paths=clip_paths,
            voiceover_path=voiceover_path,
            subtitle_path=subtitle_path,
            final_video_path=final_video_path,
            thumbnail_path=thumbnail_path,
            metadata_path=metadata_path,
        )
        dump_json(run_dir / "manifest.json", manifest.model_dump(mode="json"))
        return manifest

    def run(self, forced_topic: str | None = None) -> PipelineResult:
        run_dir = self._make_run_dir()
        assets_dir = ensure_dir(run_dir / "assets")
        images_dir = ensure_dir(assets_dir / "images")
        clips_dir = ensure_dir(assets_dir / "clips")
        audio_dir = ensure_dir(assets_dir / "audio")
        output_dir = ensure_dir(run_dir / "output")
        metadata_dir = ensure_dir(run_dir / "metadata")

        topic = self.topic_research.choose_topic()
        if forced_topic:
            topic.title = forced_topic

        script = self.script_writer.write(topic)
        scenes = self.scene_planner.plan(script)

        image_paths = self.visual_generator.generate(scenes, images_dir)
        clip_paths = self.clip_generator.generate(scenes, image_paths, clips_dir)

        narration_text = "\n".join(scene.narration for scene in scenes)
        voiceover_path = self.voiceover_generator.generate(
            narration_text=narration_text,
            duration_seconds=self.settings.total_duration_seconds,
            output_dir=audio_dir,
        )

        subtitle_path = self.animation_composer.build_subtitles(scenes, output_dir / "captions.srt")

        final_video_path, thumbnail_path = self.video_editor.assemble(
            clip_paths=clip_paths,
            voiceover_path=voiceover_path,
            subtitle_path=subtitle_path,
            output_dir=output_dir,
        )

        metadata_path = self.youtube_optimizer.generate(
            topic=topic,
            script=script,
            scenes=scenes,
            output_path=metadata_dir / "youtube_metadata.json",
        )

        manifest = self._build_manifest(
            run_dir,
            topic,
            script,
            scenes,
            image_paths,
            clip_paths,
            voiceover_path,
            subtitle_path,
            final_video_path,
            thumbnail_path,
            metadata_path,
        )

        return PipelineResult(run_dir=run_dir, assets=manifest)
