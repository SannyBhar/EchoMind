"""Experiment comparison output contracts for simulation-based cue ranking."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from echomind.scoring.models import ScoreBreakdown


class GroupScoreSummary(BaseModel):
    """Score summary for one experiment group."""

    group_key: str
    cue_ids: list[str] = Field(default_factory=list)
    count: int
    avg_composite_score: float
    max_composite_score: float
    min_composite_score: float


class DimensionComparison(BaseModel):
    """Grouped comparison for one experiment dimension."""

    dimension: str
    groups: list[GroupScoreSummary]


class ExperimentComparisonReport(BaseModel):
    """Ranked cue scores plus grouped experiment comparisons."""

    experiment_id: str
    ranked_cues: list[ScoreBreakdown]
    grouped_comparisons: list[DimensionComparison]
    metadata: dict[str, str | int | float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Multi-memory experiment models
# ---------------------------------------------------------------------------


class MemoryExperimentResult(BaseModel):
    """Experiment results for a single memory within a multi-memory run."""

    memory_id: str
    memory_title: str
    experiment_id: str
    ranked_cues: list[ScoreBreakdown]
    grouped_comparisons: list[DimensionComparison]
    metadata: dict[str, str | int | float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AggregatedGroupStats(BaseModel):
    """Cross-memory aggregated statistics for one group within a dimension."""

    group_key: str
    memory_count: int
    total_cues: int
    mean_avg_composite_score: float
    max_avg_composite_score: float
    min_avg_composite_score: float


class AggregatedDimensionSummary(BaseModel):
    """Cross-memory aggregated comparison for one experiment dimension."""

    dimension: str
    groups: list[AggregatedGroupStats]


class MultiMemoryExperimentReport(BaseModel):
    """Aggregate experiment report across all memories in a dataset run."""

    run_id: str
    memory_count: int
    per_memory_results: list[MemoryExperimentResult]
    aggregated_comparisons: list[AggregatedDimensionSummary]
    dataset_metadata: dict[str, str | int | float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
