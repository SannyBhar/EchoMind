from echomind.cues.planner import (
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.dashboard.service import collect_stimulus_artifact_previews
from echomind.dashboard.view_models import cue_variant_rows
from echomind.media.renderer import DeterministicMediaRenderer


def test_cue_variant_rows_match_variant_count() -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request=request, context=context)

    rows = cue_variant_rows(variants)

    assert len(rows) == len(variants)
    assert rows[0]["cue_id"] == variants[0].cue_id


def test_collect_stimulus_artifact_previews_reads_written_artifacts(tmp_path) -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request=request, context=context)

    renderer = DeterministicMediaRenderer(artifact_root=tmp_path / "media")
    manifest = renderer.render_manifest(memory_id=request.memory_id, variants=variants)

    previews = collect_stimulus_artifact_previews(manifest.stimuli[0])

    assert previews
    assert all(preview.exists for preview in previews)
