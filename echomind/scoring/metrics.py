"""Transparent scoring submetrics for simulation-based cue comparison."""

from __future__ import annotations

from echomind.cues.contracts import CueDeliveryMode, CueVariantSpec
from echomind.tribe.client import TribeRawOutput


def response_strength(
    cue_id: str,
    raw_outputs: list[TribeRawOutput],
    aggregate_scores: dict[str, float],
) -> float:
    """Model-derived response-strength proxy from available inference outputs."""

    matched_scores = [output.response_score for output in raw_outputs if output.cue_id == cue_id]
    if matched_scores:
        return sum(matched_scores) / len(matched_scores)

    return aggregate_scores.get(cue_id, 0.0)


def modality_factor(delivery_mode: CueDeliveryMode) -> float:
    """Heuristic modality structure factor.

    This is an explicit heuristic for comparison analysis and not a neural metric.
    """

    factors = {
        CueDeliveryMode.TEXT_ONLY: 1.00,
        CueDeliveryMode.NARRATION: 1.05,
        CueDeliveryMode.SLIDESHOW_NARRATION: 1.10,
    }
    return factors[delivery_mode]


def personalization_factor(variant: CueVariantSpec) -> float:
    """Heuristic personalization factor based on explicit cue metadata/level.

    This factor is metadata-derived and intentionally separate from model-derived signals.
    """

    level = str(variant.personalization_level).lower()
    base = {
        "low": 1.00,
        "medium": 1.06,
        "high": 1.12,
    }.get(level, 1.00)

    people_used = variant.metadata.get("people_used", [])
    place_used = variant.metadata.get("place_used")

    bonus = 0.0
    if isinstance(people_used, list) and people_used:
        bonus += 0.01
    if place_used:
        bonus += 0.01

    return min(base + bonus, 1.20)
