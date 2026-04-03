"""Scoring domain models for transparent simulation-based cue comparison."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from echomind.cues.contracts import CueDeliveryMode


class ScoringWeights(BaseModel):
    """Explicit weights used in composite score computation."""

    response_strength: float = 0.7
    modality_factor: float = 0.15
    personalization_factor: float = 0.15

    @model_validator(mode="after")
    def validate_weights(self) -> ScoringWeights:
        """Require non-negative weights and non-zero total weight."""

        weights = [self.response_strength, self.modality_factor, self.personalization_factor]
        if any(weight < 0 for weight in weights):
            raise ValueError("Scoring weights must be non-negative")
        if sum(weights) == 0:
            raise ValueError("At least one scoring weight must be positive")
        return self


class ScoreBreakdown(BaseModel):
    """Named submetrics and contributions for one cue variant."""

    cue_id: str
    delivery_mode: CueDeliveryMode
    tone: str
    personalization_level: str
    response_strength: float
    modality_factor: float
    personalization_factor: float
    composite_score: float
    contribution_response_strength: float
    contribution_modality_factor: float
    contribution_personalization_factor: float
    explanation: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScoringReport(BaseModel):
    """Scoring output for a set of cue variants."""

    report_id: str
    scores: list[ScoreBreakdown]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
