"""Deterministic media renderer for MVP cue outputs."""

from __future__ import annotations

from pathlib import Path

from echomind.cues.contracts import (
    CueDeliveryMode,
    CueMetadataKey,
    CueVariantSpec,
    RenderedStimulus,
    StimulusManifest,
)
from echomind.cues.planner import (
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.media.manifests import RENDER_VERSION, cue_artifact_dir, ensure_artifact_root
from echomind.media.slideshow import SlideshowRendererAdapter, StubSlideshowRenderer
from echomind.media.tts import StubTTSAdapter, TTSAdapter


class MediaRenderingError(RuntimeError):
    """Raised when a cue variant cannot be rendered deterministically."""


class DeterministicMediaRenderer:
    """Render cue variants into deterministic local artifacts and stimulus contracts."""

    def __init__(
        self,
        artifact_root: str | Path = "artifacts/media",
        tts_adapter: TTSAdapter | None = None,
        slideshow_adapter: SlideshowRendererAdapter | None = None,
        render_version: str = RENDER_VERSION,
    ) -> None:
        self.artifact_root = ensure_artifact_root(artifact_root)
        self.tts_adapter = tts_adapter or StubTTSAdapter()
        self.slideshow_adapter = slideshow_adapter or StubSlideshowRenderer()
        self.render_version = render_version

    def render_manifest(
        self,
        memory_id: str,
        variants: list[CueVariantSpec],
        manifest_id: str | None = None,
    ) -> StimulusManifest:
        """Render a list of planned variants into a validated stimulus manifest."""

        stimuli = [self.render_variant(variant) for variant in variants]

        metadata = {
            CueMetadataKey.TEMPLATE_VERSION.value: self.render_version,
            CueMetadataKey.VARIANT_FAMILY.value: "render_manifest",
            CueMetadataKey.SEED.value: variants[0].metadata.get(CueMetadataKey.SEED.value, 0)
            if variants
            else 0,
            CueMetadataKey.PLANNING_VERSION.value: variants[0].metadata.get(
                CueMetadataKey.PLANNING_VERSION.value,
                "unknown",
            )
            if variants
            else "unknown",
            CueMetadataKey.PEOPLE_USED.value: variants[0].metadata.get(
                CueMetadataKey.PEOPLE_USED.value,
                [],
            )
            if variants
            else [],
            CueMetadataKey.PLACE_USED.value: variants[0].metadata.get(
                CueMetadataKey.PLACE_USED.value
            )
            if variants
            else None,
        }

        return StimulusManifest(
            manifest_id=manifest_id or f"manifest-{memory_id}",
            memory_id=memory_id,
            stimuli=stimuli,
            metadata=metadata,
        )

    def render_variant(self, variant: CueVariantSpec) -> RenderedStimulus:
        """Render one cue variant into a validated stimulus output."""

        artifact_dir = cue_artifact_dir(self.artifact_root, variant.memory_id, variant.cue_id)
        base_metadata = {
            **variant.metadata,
            "render_version": self.render_version,
            "artifact_dir": str(artifact_dir),
        }

        if variant.delivery_mode == CueDeliveryMode.TEXT_ONLY:
            text_path = artifact_dir / "text_prompt.txt"
            text_path.write_text(variant.script_text, encoding="utf-8")

            return RenderedStimulus(
                stimulus_id=f"stimulus-{variant.cue_id}",
                cue_id=variant.cue_id,
                delivery_mode=variant.delivery_mode,
                text_payload=variant.script_text,
                metadata={**base_metadata, "text_artifact": str(text_path)},
            )

        if variant.delivery_mode == CueDeliveryMode.NARRATION:
            if not variant.narration_text:
                raise MediaRenderingError(f"Narration cue missing narration_text: {variant.cue_id}")

            script_path = artifact_dir / "narration_script.txt"
            script_path.write_text(variant.narration_text, encoding="utf-8")

            audio_path = artifact_dir / "narration.wav"
            self.tts_adapter.synthesize(variant.narration_text, audio_path)

            return RenderedStimulus(
                stimulus_id=f"stimulus-{variant.cue_id}",
                cue_id=variant.cue_id,
                delivery_mode=variant.delivery_mode,
                narration_transcript=variant.narration_text,
                narration_audio_uri=str(audio_path),
                metadata={
                    **base_metadata,
                    "narration_script_artifact": str(script_path),
                    "narration_audio_artifact": str(audio_path),
                },
            )

        if variant.delivery_mode == CueDeliveryMode.SLIDESHOW_NARRATION:
            if not variant.narration_text:
                raise MediaRenderingError(
                    f"Slideshow cue missing narration_text: {variant.cue_id}"
                )

            image_uris = _extract_image_uris(variant.slide_image_prompts)
            if not image_uris:
                raise MediaRenderingError(
                    f"Slideshow cue missing usable image references: {variant.cue_id}"
                )

            script_path = artifact_dir / "slideshow_narration_script.txt"
            script_path.write_text(variant.narration_text, encoding="utf-8")

            audio_path = artifact_dir / "slideshow_narration.wav"
            self.tts_adapter.synthesize(variant.narration_text, audio_path)

            plan_path = artifact_dir / "slideshow_plan.json"
            video_path = artifact_dir / "slideshow.mp4"
            self.slideshow_adapter.render(
                image_uris=image_uris,
                narration_audio_uri=str(audio_path),
                output_video_path=video_path,
                output_plan_path=plan_path,
            )

            return RenderedStimulus(
                stimulus_id=f"stimulus-{variant.cue_id}",
                cue_id=variant.cue_id,
                delivery_mode=variant.delivery_mode,
                narration_transcript=variant.narration_text,
                narration_audio_uri=str(audio_path),
                slide_image_uris=image_uris,
                metadata={
                    **base_metadata,
                    "slideshow_script_artifact": str(script_path),
                    "slideshow_audio_artifact": str(audio_path),
                    "slideshow_plan_artifact": str(plan_path),
                    "slideshow_video_artifact": str(video_path),
                },
            )

        raise MediaRenderingError(f"Unsupported cue delivery mode: {variant.delivery_mode}")


def render_demo_planner_outputs(artifact_root: str | Path = "artifacts/media") -> StimulusManifest:
    """Render deterministic artifacts from the built-in demo planner context."""

    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    renderer = DeterministicMediaRenderer(artifact_root=artifact_root)
    return renderer.render_manifest(
        memory_id=request.memory_id,
        variants=variants,
        manifest_id=f"manifest-{request.memory_id}-demo",
    )


def _extract_image_uris(slide_image_prompts: list[str]) -> list[str]:
    """Extract deterministic image URIs from planner prompts."""

    prefix = "Use reference image: "
    image_uris: list[str] = []
    for prompt in slide_image_prompts:
        if prompt.startswith(prefix):
            uri = prompt[len(prefix) :].strip()
            if uri:
                image_uris.append(uri)
    # Keep stable, deduplicated ordering.
    return sorted(dict.fromkeys(image_uris))
