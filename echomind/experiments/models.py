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
