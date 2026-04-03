"""Human-readable explanation helpers for cue scoring."""

from __future__ import annotations


def build_score_explanation(
    response_strength_value: float,
    modality_factor_value: float,
    personalization_factor_value: float,
    response_contribution: float,
    modality_contribution: float,
    personalization_contribution: float,
) -> str:
    """Build decomposable explanation text for one cue score."""

    contributions = {
        "response_strength": response_contribution,
        "modality_factor": modality_contribution,
        "personalization_factor": personalization_contribution,
    }
    top_driver = max(contributions, key=contributions.get)

    return (
        f"Top contribution: {top_driver}. "
        f"response_strength={response_strength_value:.4f}, "
        f"modality_factor={modality_factor_value:.4f}, "
        f"personalization_factor={personalization_factor_value:.4f}."
    )
