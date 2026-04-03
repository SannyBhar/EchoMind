"""Experiment report assembly and deterministic demo-comparison helpers."""

from __future__ import annotations

import json
from pathlib import Path

from echomind.cues.contracts import CueDeliveryMode
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
from echomind.experiments.models import ExperimentComparisonReport
from echomind.media.renderer import DeterministicMediaRenderer
from echomind.scoring.models import ScoringReport
from echomind.scoring.pipeline import score_cue_variants
from echomind.tribe.infer import run_tribe_inference


def build_experiment_report(
    experiment_id: str,
    score_report: ScoringReport,
) -> ExperimentComparisonReport:
    """Build ranked and grouped comparison views from one scoring report."""

    ranked = rank_scores(score_report)
    grouped = [
        compare_personalized_vs_generic(ranked),
        compare_warm_vs_neutral(ranked),
        compare_delivery_modes(ranked),
    ]

    return ExperimentComparisonReport(
        experiment_id=experiment_id,
        ranked_cues=ranked,
        grouped_comparisons=grouped,
        metadata={
            "score_count": len(ranked),
            "top_cue_id": ranked[0].cue_id if ranked else "",
            "top_composite_score": ranked[0].composite_score if ranked else 0.0,
        },
    )


def run_demo_experiment_comparison(
    artifact_root: str | Path = "artifacts/experiments",
    supported_modalities: set[CueDeliveryMode] | None = None,
) -> ExperimentComparisonReport:
    """Run deterministic demo comparison from planner to grouped score report."""

    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    root = Path(artifact_root)
    renderer = DeterministicMediaRenderer(artifact_root=root / "media")
    manifest = renderer.render_manifest(
        memory_id=request.memory_id,
        variants=variants,
        manifest_id=f"manifest-{request.memory_id}-experiment",
    )

    inference_result = run_tribe_inference(
        manifest=manifest,
        request_id=f"{request.request_id}-experiment",
        artifact_root=root / "inference",
        supported_modalities=supported_modalities or {CueDeliveryMode.TEXT_ONLY},
    )

    score_report = score_cue_variants(
        report_id=f"score-{request.request_id}",
        variants=variants,
        inference_summary=inference_result.summary,
        raw_outputs=inference_result.raw_outputs,
    )

    report = build_experiment_report(
        experiment_id=f"experiment-{request.request_id}",
        score_report=score_report,
    )
    save_experiment_report(report=report, artifact_root=root)
    return report


def save_experiment_report(
    report: ExperimentComparisonReport,
    artifact_root: str | Path,
) -> Path:
    """Persist experiment comparison report to deterministic local artifacts."""

    root = Path(artifact_root)
    out_dir = root / "reports" / _sanitize_id(report.experiment_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "comparison_report.json"
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )
    return report_path


def _sanitize_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value)
