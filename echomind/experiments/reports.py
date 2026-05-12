"""Experiment report assembly and deterministic demo-comparison helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from echomind.cues.contracts import CueDeliveryMode, CueGenerationRequest
from echomind.cues.planner import (
    PlannerMemoryContext,
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.experiments.aggregate import aggregate_multi_memory_comparisons
from echomind.experiments.compare import (
    compare_delivery_modes,
    compare_personalized_vs_generic,
    compare_warm_vs_neutral,
    rank_scores,
)
from echomind.experiments.models import (
    ExperimentComparisonReport,
    MemoryExperimentResult,
    MultiMemoryExperimentReport,
)
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


# ---------------------------------------------------------------------------
# Multi-memory experiment helpers
# ---------------------------------------------------------------------------


def run_memory_experiment(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
    artifact_root: str | Path = "artifacts/experiments",
    supported_modalities: set[CueDeliveryMode] | None = None,
) -> MemoryExperimentResult:
    """Run the full pipeline for one memory and return a MemoryExperimentResult.

    Executes: plan -> render -> TRIBE smoke inference -> score -> group comparisons.
    All artifacts are written under artifact_root for auditability.
    """
    root = Path(artifact_root)
    variants = plan_deterministic_mvp_variants(request, context)

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

    ranked = rank_scores(score_report)
    grouped = [
        compare_personalized_vs_generic(ranked),
        compare_warm_vs_neutral(ranked),
        compare_delivery_modes(ranked),
    ]

    return MemoryExperimentResult(
        memory_id=request.memory_id,
        memory_title=request.memory_title,
        experiment_id=f"experiment-{request.request_id}",
        ranked_cues=ranked,
        grouped_comparisons=grouped,
        metadata={
            "score_count": len(ranked),
            "top_cue_id": ranked[0].cue_id if ranked else "",
            "top_composite_score": ranked[0].composite_score if ranked else 0.0,
        },
    )


def run_multi_memory_experiment(
    dataset: list[tuple[CueGenerationRequest, PlannerMemoryContext]],
    run_id: str = "multi-memory-experiment",
    artifact_root: str | Path = "artifacts/experiments",
    supported_modalities: set[CueDeliveryMode] | None = None,
) -> MultiMemoryExperimentReport:
    """Run the full pipeline across a multi-memory dataset and return aggregate report.

    For each memory: plan -> render -> TRIBE smoke -> score -> per-memory result.
    Aggregates all results into cross-memory dimension comparisons.
    Per-memory and aggregate artifacts are written under artifact_root.

    Note: TRIBE execution uses the deterministic stub client by default.
    Scoring includes explicit heuristic factors for modality and personalization;
    these are labeled as simulation heuristics, not model-derived measures.
    """
    root = Path(artifact_root)
    per_memory_results: list[MemoryExperimentResult] = []

    for request, context in dataset:
        memory_root = root / "per_memory" / request.memory_id
        result = run_memory_experiment(
            request=request,
            context=context,
            artifact_root=memory_root,
            supported_modalities=supported_modalities,
        )
        # Persist per-memory comparison report alongside other artifacts.
        save_experiment_report(
            report=ExperimentComparisonReport(
                experiment_id=result.experiment_id,
                ranked_cues=result.ranked_cues,
                grouped_comparisons=result.grouped_comparisons,
                metadata=result.metadata,
            ),
            artifact_root=memory_root,
        )
        per_memory_results.append(result)

    aggregated = aggregate_multi_memory_comparisons(per_memory_results)

    report = MultiMemoryExperimentReport(
        run_id=run_id,
        memory_count=len(per_memory_results),
        per_memory_results=per_memory_results,
        aggregated_comparisons=aggregated,
        dataset_metadata={
            "total_memories": len(per_memory_results),
            "pipeline_version": "mvp.v1",
            "tribe_path": "text_only_smoke",
        },
    )
    save_multi_memory_report(report=report, artifact_root=root)
    return report


def save_multi_memory_report(
    report: MultiMemoryExperimentReport,
    artifact_root: str | Path,
) -> dict[str, Path]:
    """Persist multi-memory report as JSON and dimension summary as CSV.

    Returns a dict with keys 'json' and 'csv' pointing to written artifact paths.
    """
    root = Path(artifact_root)
    out_dir = root / "aggregate"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "multi_memory_report.json"
    json_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )

    csv_path = out_dir / "dimension_summary.csv"
    _write_dimension_csv(report, csv_path)

    return {"json": json_path, "csv": csv_path}


def _write_dimension_csv(report: MultiMemoryExperimentReport, path: Path) -> None:
    rows = []
    for dim in report.aggregated_comparisons:
        for grp in dim.groups:
            rows.append(
                {
                    "run_id": report.run_id,
                    "dimension": dim.dimension,
                    "group_key": grp.group_key,
                    "memory_count": grp.memory_count,
                    "total_cues": grp.total_cues,
                    "mean_avg_composite_score": grp.mean_avg_composite_score,
                    "max_avg_composite_score": grp.max_avg_composite_score,
                    "min_avg_composite_score": grp.min_avg_composite_score,
                }
            )

    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _sanitize_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value)
