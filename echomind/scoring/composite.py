"""Composite score assembly for transparent cue comparison."""

from __future__ import annotations

from echomind.scoring.models import ScoringWeights


def composite_score(
    response_strength_value: float,
    modality_factor_value: float,
    personalization_factor_value: float,
    weights: ScoringWeights,
) -> tuple[float, float, float, float]:
    """Return composite score and explicit weighted contributions.

    Modality/personalization factors are transformed into deltas from 1.0 so
    heuristic factors remain clearly separated from model-derived strength.
    """

    total = (
        weights.response_strength
        + weights.modality_factor
        + weights.personalization_factor
    )

    response_component = weights.response_strength * response_strength_value
    modality_component = weights.modality_factor * max(modality_factor_value - 1.0, 0.0)
    personalization_component = (
        weights.personalization_factor * max(personalization_factor_value - 1.0, 0.0)
    )

    combined = (response_component + modality_component + personalization_component) / total
    combined = min(max(combined, 0.0), 1.0)

    return combined, response_component, modality_component, personalization_component
