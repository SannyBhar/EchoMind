"""Deterministic experiment grouping helpers for cue-score comparisons."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from echomind.experiments.models import DimensionComparison, GroupScoreSummary
from echomind.scoring.models import ScoreBreakdown, ScoringReport


def rank_scores(report: ScoringReport) -> list[ScoreBreakdown]:
    """Return score entries in descending composite order."""

    return sorted(report.scores, key=lambda item: item.composite_score, reverse=True)


def compare_personalized_vs_generic(scores: list[ScoreBreakdown]) -> DimensionComparison:
    """Compare personalized vs generic cue groups."""

    def group_key(item: ScoreBreakdown) -> str:
        level = item.personalization_level.lower()
        return "generic" if level == "low" else "personalized"

    return _summarize_dimension(scores, "personalized_vs_generic", group_key)


def compare_warm_vs_neutral(scores: list[ScoreBreakdown]) -> DimensionComparison:
    """Compare warm vs neutral cue groups."""

    def group_key(item: ScoreBreakdown) -> str:
        tone = item.tone.lower()
        if tone in {"warm", "neutral"}:
            return tone
        return "other"

    return _summarize_dimension(scores, "warm_vs_neutral", group_key)


def compare_delivery_modes(scores: list[ScoreBreakdown]) -> DimensionComparison:
    """Compare grouped cue scores by delivery mode."""

    return _summarize_dimension(scores, "delivery_mode", lambda item: item.delivery_mode.value)


def _summarize_dimension(
    scores: list[ScoreBreakdown],
    dimension: str,
    key_func: Callable[[ScoreBreakdown], str],
) -> DimensionComparison:
    grouped: dict[str, list[ScoreBreakdown]] = defaultdict(list)
    for score in scores:
        grouped[key_func(score)].append(score)

    group_summaries: list[GroupScoreSummary] = []
    for group_key, items in sorted(grouped.items()):
        values = [item.composite_score for item in items]
        group_summaries.append(
            GroupScoreSummary(
                group_key=group_key,
                cue_ids=[item.cue_id for item in items],
                count=len(items),
                avg_composite_score=sum(values) / len(values),
                max_composite_score=max(values),
                min_composite_score=min(values),
            )
        )

    return DimensionComparison(dimension=dimension, groups=group_summaries)
