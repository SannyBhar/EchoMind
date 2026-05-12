"""Cross-memory aggregation helpers for multi-memory experiment reports."""

from __future__ import annotations

from collections import defaultdict

from echomind.experiments.models import (
    AggregatedDimensionSummary,
    AggregatedGroupStats,
    MemoryExperimentResult,
)

_DIMENSIONS = ("personalized_vs_generic", "warm_vs_neutral", "delivery_mode")


def aggregate_dimension_across_memories(
    results: list[MemoryExperimentResult],
    dimension: str,
) -> AggregatedDimensionSummary:
    """Aggregate one comparison dimension across all per-memory results.

    For each group_key within the dimension, collects each memory's
    avg_composite_score and computes mean/max/min across memories.
    """
    group_avgs: dict[str, list[float]] = defaultdict(list)
    group_cue_counts: dict[str, int] = defaultdict(int)

    for result in results:
        for comparison in result.grouped_comparisons:
            if comparison.dimension != dimension:
                continue
            for group in comparison.groups:
                group_avgs[group.group_key].append(group.avg_composite_score)
                group_cue_counts[group.group_key] += group.count

    groups: list[AggregatedGroupStats] = []
    for key in sorted(group_avgs.keys()):
        avgs = group_avgs[key]
        groups.append(
            AggregatedGroupStats(
                group_key=key,
                memory_count=len(avgs),
                total_cues=group_cue_counts[key],
                mean_avg_composite_score=round(sum(avgs) / len(avgs), 6),
                max_avg_composite_score=round(max(avgs), 6),
                min_avg_composite_score=round(min(avgs), 6),
            )
        )

    return AggregatedDimensionSummary(dimension=dimension, groups=groups)


def aggregate_multi_memory_comparisons(
    results: list[MemoryExperimentResult],
) -> list[AggregatedDimensionSummary]:
    """Aggregate all three comparison dimensions across memories."""
    return [aggregate_dimension_across_memories(results, dim) for dim in _DIMENSIONS]
