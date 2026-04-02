"""Slideshow rendering adapter contracts and deterministic stub implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol


class SlideshowRendererAdapter(Protocol):
    """Pluggable slideshow/video adapter interface."""

    def render(
        self,
        image_uris: list[str],
        narration_audio_uri: str,
        output_video_path: Path,
        output_plan_path: Path,
    ) -> Path:
        """Render slideshow plan and return output video path."""


class StubSlideshowRenderer:
    """Deterministic slideshow stub writing ffmpeg-compatible plan metadata."""

    def render(
        self,
        image_uris: list[str],
        narration_audio_uri: str,
        output_video_path: Path,
        output_plan_path: Path,
    ) -> Path:
        output_video_path.parent.mkdir(parents=True, exist_ok=True)

        plan_payload = {
            "renderer": "stub_slideshow",
            "ffmpeg_compatible": True,
            "image_uris": image_uris,
            "narration_audio_uri": narration_audio_uri,
        }
        output_plan_path.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")

        output_video_path.write_text(
            "STUB_MP4\n"
            f"frames={len(image_uris)}\n"
            f"audio={narration_audio_uri}\n",
            encoding="utf-8",
        )
        return output_video_path
