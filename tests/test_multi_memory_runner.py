"""Tests for the multi-memory experiment runner, aggregate helpers, and report assembly."""

from __future__ import annotations

from pathlib import Path

import pytest

from echomind.demo_data.loader import load_demo_dataset
from echomind.demo_data.memories import DEMO_MEMORIES
from echomind.experiments.aggregate import (
    aggregate_dimension_across_memories,
    aggregate_multi_memory_comparisons,
)
from echomind.experiments.models import (
    AggregatedDimensionSummary,
    MemoryExperimentResult,
    MultiMemoryExperimentReport,
)
from echomind.experiments.reports import (
    run_memory_experiment,
    run_multi_memory_experiment,
    save_multi_memory_report,
)
from echomind.experiments.runner import MultiMemoryExperimentConfig, MultiMemoryExperimentRunner


# ---------------------------------------------------------------------------
# Helpers — build a small subset for fast tests
# ---------------------------------------------------------------------------


def _two_memory_dataset() -> list:
    """Return just the first two demo memories for fast in-test execution."""
    return load_demo_dataset()[:2]


def _run_single_memory(tmp_path: Path) -> MemoryExperimentResult:
    dataset = _two_memory_dataset()
    req, ctx = dataset[0]
    return run_memory_experiment(request=req, context=ctx, artifact_root=tmp_path / "exp")


# ---------------------------------------------------------------------------
# run_memory_experiment
# ---------------------------------------------------------------------------


def test_run_memory_experiment_returns_result(tmp_path: Path) -> None:
    result = _run_single_memory(tmp_path)
    assert isinstance(result, MemoryExperimentResult)
    assert result.memory_id == DEMO_MEMORIES[0].memory_id
    assert result.memory_title == DEMO_MEMORIES[0].title
    assert result.ranked_cues
    assert len(result.grouped_comparisons) == 3


def test_run_memory_experiment_ranked_cues_are_descending(tmp_path: Path) -> None:
    result = _run_single_memory(tmp_path)
    scores = [c.composite_score for c in result.ranked_cues]
    assert scores == sorted(scores, reverse=True)


def test_run_memory_experiment_grouped_comparison_dimensions(tmp_path: Path) -> None:
    result = _run_single_memory(tmp_path)
    dims = {c.dimension for c in result.grouped_comparisons}
    assert dims == {"personalized_vs_generic", "warm_vs_neutral", "delivery_mode"}


def test_run_memory_experiment_writes_artifacts(tmp_path: Path) -> None:
    result = _run_single_memory(tmp_path)
    # Media and inference artifacts should exist under the per-memory root.
    media_dir = tmp_path / "exp" / "media"
    inference_dir = tmp_path / "exp" / "inference"
    assert media_dir.exists()
    assert inference_dir.exists()


# ---------------------------------------------------------------------------
# run_multi_memory_experiment
# ---------------------------------------------------------------------------


def test_run_multi_memory_experiment_two_memories(tmp_path: Path) -> None:
    dataset = _two_memory_dataset()
    report = run_multi_memory_experiment(
        dataset=dataset,
        run_id="test-run",
        artifact_root=tmp_path / "multi",
    )
    assert isinstance(report, MultiMemoryExperimentReport)
    assert report.memory_count == 2
    assert len(report.per_memory_results) == 2


def test_run_multi_memory_experiment_aggregated_comparisons(tmp_path: Path) -> None:
    dataset = _two_memory_dataset()
    report = run_multi_memory_experiment(
        dataset=dataset,
        run_id="test-run",
        artifact_root=tmp_path / "multi",
    )
    dims = {d.dimension for d in report.aggregated_comparisons}
    assert dims == {"personalized_vs_generic", "warm_vs_neutral", "delivery_mode"}


def test_run_multi_memory_experiment_writes_aggregate_artifacts(tmp_path: Path) -> None:
    dataset = _two_memory_dataset()
    run_multi_memory_experiment(
        dataset=dataset,
        run_id="test-run",
        artifact_root=tmp_path / "multi",
    )
    assert (tmp_path / "multi" / "aggregate" / "multi_memory_report.json").exists()
    assert (tmp_path / "multi" / "aggregate" / "dimension_summary.csv").exists()


def test_run_multi_memory_experiment_writes_per_memory_reports(tmp_path: Path) -> None:
    dataset = _two_memory_dataset()
    run_multi_memory_experiment(
        dataset=dataset,
        run_id="test-run",
        artifact_root=tmp_path / "multi",
    )
    for req, _ in dataset:
        report_path = (
            tmp_path
            / "multi"
            / "per_memory"
            / req.memory_id
            / "reports"
            / f"experiment-plan-{req.memory_id}"
            / "comparison_report.json"
        )
        assert report_path.exists(), f"missing per-memory report for {req.memory_id}"


# ---------------------------------------------------------------------------
# save_multi_memory_report
# ---------------------------------------------------------------------------


def test_save_multi_memory_report_produces_csv_rows(tmp_path: Path) -> None:
    dataset = _two_memory_dataset()
    report = run_multi_memory_experiment(
        dataset=dataset,
        run_id="csv-test",
        artifact_root=tmp_path / "multi",
    )
    paths = save_multi_memory_report(report=report, artifact_root=tmp_path / "multi")
    csv_text = paths["csv"].read_text(encoding="utf-8")
    assert "dimension" in csv_text
    assert "group_key" in csv_text
    assert "mean_avg_composite_score" in csv_text


# ---------------------------------------------------------------------------
# aggregate helpers
# ---------------------------------------------------------------------------


def test_aggregate_dimension_across_memories_group_keys(tmp_path: Path) -> None:
    dataset = _two_memory_dataset()
    report = run_multi_memory_experiment(
        dataset=dataset,
        run_id="agg-test",
        artifact_root=tmp_path / "multi",
    )
    dim = aggregate_dimension_across_memories(
        report.per_memory_results, "personalized_vs_generic"
    )
    assert isinstance(dim, AggregatedDimensionSummary)
    keys = {g.group_key for g in dim.groups}
    assert keys == {"generic", "personalized"}


def test_aggregate_dimension_memory_count_matches_dataset(tmp_path: Path) -> None:
    dataset = _two_memory_dataset()
    report = run_multi_memory_experiment(
        dataset=dataset,
        run_id="agg-count-test",
        artifact_root=tmp_path / "multi",
    )
    dim = aggregate_dimension_across_memories(report.per_memory_results, "warm_vs_neutral")
    for grp in dim.groups:
        assert grp.memory_count == 2


def test_aggregate_multi_memory_comparisons_returns_three_dims(tmp_path: Path) -> None:
    dataset = _two_memory_dataset()
    report = run_multi_memory_experiment(
        dataset=dataset,
        run_id="three-dim-test",
        artifact_root=tmp_path / "multi",
    )
    summaries = aggregate_multi_memory_comparisons(report.per_memory_results)
    assert len(summaries) == 3
    dims = {s.dimension for s in summaries}
    assert dims == {"personalized_vs_generic", "warm_vs_neutral", "delivery_mode"}


# ---------------------------------------------------------------------------
# MultiMemoryExperimentRunner
# ---------------------------------------------------------------------------


def test_multi_memory_runner_produces_report(tmp_path: Path) -> None:
    config = MultiMemoryExperimentConfig(
        run_id="runner-test",
        artifact_root=str(tmp_path / "runner"),
    )
    runner = MultiMemoryExperimentRunner()
    report = runner.run(config)
    assert isinstance(report, MultiMemoryExperimentReport)
    assert report.memory_count == len(DEMO_MEMORIES)
