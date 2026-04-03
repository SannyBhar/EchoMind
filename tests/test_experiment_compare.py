from pathlib import Path

from echomind.cues.planner import (
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.experiments.compare import (
    compare_delivery_modes,
    compare_personalized_vs_generic,
    compare_warm_vs_neutral,
    rank_scores,
)
from echomind.experiments.reports import build_experiment_report, run_demo_experiment_comparison
from echomind.scoring.models import ScoringReport
from echomind.scoring.pipeline import score_cue_variants
from echomind.tribe.aggregates import build_inference_summary
from echomind.tribe.client import TribeRawOutput


def _build_scored_demo_report() -> ScoringReport:
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    raw_outputs = [
        TribeRawOutput(
            stimulus_id=f"stim-{variant.cue_id}",
            cue_id=variant.cue_id,
            response_score=(idx + 1) / 10.0,
            token_count=24,
        )
        for idx, variant in enumerate(variants)
    ]
    summary = build_inference_summary(
        request_id="req-exp-001",
        engine_name="tribe-v2",
        outputs=raw_outputs,
    )
    return score_cue_variants(
        report_id="score-exp-001",
        variants=variants,
        inference_summary=summary,
        raw_outputs=raw_outputs,
    )


def test_compare_dimensions_produce_expected_groups() -> None:
    score_report = _build_scored_demo_report()
    ranked = rank_scores(score_report)

    personal = compare_personalized_vs_generic(ranked)
    assert personal.dimension == "personalized_vs_generic"
    assert {group.group_key for group in personal.groups} == {"generic", "personalized"}

    tone = compare_warm_vs_neutral(ranked)
    assert tone.dimension == "warm_vs_neutral"
    assert {group.group_key for group in tone.groups} >= {"warm", "neutral"}

    mode = compare_delivery_modes(ranked)
    assert mode.dimension == "delivery_mode"
    assert {group.group_key for group in mode.groups} == {
        "text_only",
        "narration",
        "slideshow_narration",
    }


def test_build_experiment_report_contains_ranked_and_grouped_views() -> None:
    score_report = _build_scored_demo_report()
    report = build_experiment_report("experiment-demo", score_report=score_report)

    assert report.ranked_cues
    assert len(report.grouped_comparisons) == 3
    assert report.metadata["score_count"] == len(report.ranked_cues)
    assert report.metadata["top_cue_id"] == report.ranked_cues[0].cue_id


def test_demo_experiment_comparison_writes_report_artifact(tmp_path: Path) -> None:
    report = run_demo_experiment_comparison(artifact_root=tmp_path / "experiments")

    out_path = (
        tmp_path
        / "experiments"
        / "reports"
        / "experiment-plan-demo-memory-001"
        / "comparison_report.json"
    )
    assert report.ranked_cues
    assert out_path.exists()
