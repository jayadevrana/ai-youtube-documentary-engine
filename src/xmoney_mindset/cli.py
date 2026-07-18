from __future__ import annotations

import argparse
import json
from pathlib import Path

from xmoney_mindset.config import Settings
from xmoney_mindset.pipeline.orchestrator import XMoneyPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xmoney",
        description="Autonomous AI YouTube documentary generation pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run full generation pipeline")
    run_parser.add_argument("--topic", type=str, default=None, help="Optional forced topic/title")
    run_parser.add_argument("--duration-minutes", type=int, default=None, help="Override target video duration")
    run_parser.add_argument(
        "--real",
        action="store_true",
        help="Enable real API generation (requires configured API keys)",
    )

    return parser


def cmd_run(args: argparse.Namespace) -> int:
    settings = Settings()
    if args.duration_minutes is not None:
        settings.target_duration_minutes = args.duration_minutes
    if args.real:
        settings.enable_real_generation = True

    pipeline = XMoneyPipeline(settings)
    result = pipeline.run(forced_topic=args.topic)

    summary = {
        "run_dir": str(result.run_dir.resolve()),
        "final_video": str(result.assets.final_video_path.resolve()),
        "voiceover": str(result.assets.voiceover_path.resolve()),
        "thumbnail": str(result.assets.thumbnail_path.resolve()),
        "metadata": str(result.assets.metadata_path.resolve()),
        "scene_count": len(result.assets.scenes),
        "topic": result.assets.topic.title,
    }
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        return cmd_run(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
