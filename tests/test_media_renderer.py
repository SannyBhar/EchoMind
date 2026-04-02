from pathlib import Path

import pytest

from echomind.cues.contracts import CueDeliveryMode, CueVariantSpec
from echomind.cues.planner import (
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.media.renderer import (
    DeterministicMediaRenderer,
    MediaRenderingError,
    render_demo_planner_outputs,
)


def test_renderer_outputs_valid_manifest_for_demo_variants(tmp_path: Path) -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    renderer = DeterministicMediaRenderer(artifact_root=tmp_path)
    manifest = renderer.render_manifest(memory_id=request.memory_id, variants=variants)

    assert manifest.memory_id == request.memory_id
    assert len(manifest.stimuli) == 6

    text_stimulus = next(
        s for s in manifest.stimuli if s.delivery_mode == CueDeliveryMode.TEXT_ONLY
    )
    narration_stimulus = next(
        s for s in manifest.stimuli if s.delivery_mode == CueDeliveryMode.NARRATION
    )
    slideshow_stimulus = next(
        s for s in manifest.stimuli if s.delivery_mode == CueDeliveryMode.SLIDESHOW_NARRATION
    )

    assert text_stimulus.text_payload
    assert narration_stimulus.narration_audio_uri
    assert slideshow_stimulus.narration_audio_uri
    assert slideshow_stimulus.slide_image_uris

    assert Path(narration_stimulus.narration_audio_uri).exists()


def test_renderer_raises_for_slideshow_without_parseable_image_assets(tmp_path: Path) -> None:
    variant = CueVariantSpec(
        cue_id="cue-bad-slide",
        memory_id="memory-001",
        delivery_mode=CueDeliveryMode.SLIDESHOW_NARRATION,
        tone="neutral",
        personalization_level="high",
        script_text="Slideshow script",
        narration_text="Slideshow narration",
        slide_image_prompts=["not-a-reference-uri"],
    )

    renderer = DeterministicMediaRenderer(artifact_root=tmp_path)

    with pytest.raises(MediaRenderingError):
        renderer.render_variant(variant)


def test_demo_render_helper_builds_artifacts(tmp_path: Path) -> None:
    manifest = render_demo_planner_outputs(artifact_root=tmp_path)

    assert manifest.stimuli
    assert any(stimulus.delivery_mode == CueDeliveryMode.TEXT_ONLY for stimulus in manifest.stimuli)
    assert any(stimulus.delivery_mode == CueDeliveryMode.NARRATION for stimulus in manifest.stimuli)
    assert any(
        stimulus.delivery_mode == CueDeliveryMode.SLIDESHOW_NARRATION
        for stimulus in manifest.stimuli
    )
