import json
from pathlib import Path

from echomind.cues.contracts import CueDeliveryMode, InferenceStatus
from echomind.cues.planner import (
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.media.renderer import DeterministicMediaRenderer
from echomind.tribe.infer import run_demo_text_only_smoke_inference, run_tribe_inference
from echomind.tribe.preprocess import preprocess_manifest_for_tribe


def test_preprocess_filters_to_text_only_by_default(tmp_path: Path) -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    renderer = DeterministicMediaRenderer(artifact_root=tmp_path / "media")
    manifest = renderer.render_manifest(memory_id=request.memory_id, variants=variants)

    batch = preprocess_manifest_for_tribe(manifest=manifest, request_id="req-preprocess")

    assert batch.stimuli
    assert all(item.modality == CueDeliveryMode.TEXT_ONLY for item in batch.stimuli)


def test_run_tribe_inference_persists_outputs(tmp_path: Path) -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    renderer = DeterministicMediaRenderer(artifact_root=tmp_path / "media")
    manifest = renderer.render_manifest(memory_id=request.memory_id, variants=variants)

    result = run_tribe_inference(
        manifest=manifest,
        request_id="tribe-run-001",
        artifact_root=tmp_path / "inference",
        supported_modalities={CueDeliveryMode.TEXT_ONLY},
    )

    assert result.summary.status == InferenceStatus.SUCCEEDED
    assert result.raw_outputs
    assert result.summary.summary_metadata["stimulus_count"] == len(result.raw_outputs)
    assert result.summary.summary_metadata["run_dir"]
    assert result.artifacts.request_path.exists()
    assert result.artifacts.raw_outputs_path.exists()
    assert result.artifacts.summary_path.exists()
    assert result.artifacts.metadata_path.exists()

    metadata = json.loads(result.artifacts.metadata_path.read_text(encoding="utf-8"))
    assert metadata["request_id"] == "tribe-run-001"


def test_demo_text_only_smoke_inference_path(tmp_path: Path) -> None:
    result = run_demo_text_only_smoke_inference(artifact_root=tmp_path / "smoke")

    assert result.summary.status == InferenceStatus.SUCCEEDED
    assert result.summary.ranked_cue_ids
    assert result.artifacts.run_dir.exists()
