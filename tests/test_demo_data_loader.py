"""Tests for the synthetic demo dataset definitions and loader."""

from __future__ import annotations

from echomind.cues.contracts import CueDeliveryMode, CueGenerationRequest
from echomind.cues.planner import PlannerMemoryContext
from echomind.demo_data.loader import (
    build_context_from_spec,
    build_request_from_spec,
    list_demo_memory_ids,
    list_demo_memory_specs,
    load_demo_dataset,
    load_demo_dataset_by_category,
)
from echomind.demo_data.memories import DEMO_MEMORIES, DEMO_MEMORY_CATEGORIES


# ---------------------------------------------------------------------------
# Dataset definitions
# ---------------------------------------------------------------------------


def test_dataset_has_expected_count() -> None:
    assert len(DEMO_MEMORIES) == 12


def test_all_memory_ids_are_unique() -> None:
    ids = [m.memory_id for m in DEMO_MEMORIES]
    assert len(ids) == len(set(ids))


def test_all_seeds_are_unique() -> None:
    seeds = [m.seed for m in DEMO_MEMORIES]
    assert len(seeds) == len(set(seeds))


def test_each_memory_has_required_fields() -> None:
    for spec in DEMO_MEMORIES:
        assert spec.memory_id.startswith("demo-")
        assert spec.title
        assert spec.summary
        assert len(spec.people_names) >= 1
        assert spec.place_name
        assert len(spec.image_asset_uris) >= 1
        assert spec.category


def test_image_uris_are_demo_prefixed() -> None:
    for spec in DEMO_MEMORIES:
        for uri in spec.image_asset_uris:
            assert uri.startswith("s3://demo-assets/"), f"unexpected uri: {uri}"


def test_categories_cover_variety() -> None:
    assert len(DEMO_MEMORY_CATEGORIES) >= 6, "expected at least 6 distinct categories"


def test_no_category_over_represented() -> None:
    from collections import Counter
    counts = Counter(m.category for m in DEMO_MEMORIES)
    for category, count in counts.items():
        assert count <= 3, f"category '{category}' has {count} memories (max 3)"


# ---------------------------------------------------------------------------
# Builder helpers
# ---------------------------------------------------------------------------


def test_build_context_from_spec_round_trips_fields() -> None:
    spec = DEMO_MEMORIES[0]
    ctx = build_context_from_spec(spec)
    assert isinstance(ctx, PlannerMemoryContext)
    assert ctx.memory_id == spec.memory_id
    assert ctx.memory_title == spec.title
    assert ctx.memory_summary == spec.summary
    assert ctx.people_names == list(spec.people_names)
    assert ctx.place_name == spec.place_name
    assert ctx.image_asset_uris == list(spec.image_asset_uris)


def test_build_request_from_spec_sets_all_modes() -> None:
    spec = DEMO_MEMORIES[0]
    req = build_request_from_spec(spec)
    assert isinstance(req, CueGenerationRequest)
    assert req.memory_id == spec.memory_id
    assert req.request_id == f"plan-{spec.memory_id}"
    assert CueDeliveryMode.TEXT_ONLY in req.target_modes
    assert CueDeliveryMode.NARRATION in req.target_modes
    assert CueDeliveryMode.SLIDESHOW_NARRATION in req.target_modes
    assert req.seed == spec.seed


# ---------------------------------------------------------------------------
# Loader functions
# ---------------------------------------------------------------------------


def test_load_demo_dataset_returns_all_pairs() -> None:
    pairs = load_demo_dataset()
    assert len(pairs) == len(DEMO_MEMORIES)
    for req, ctx in pairs:
        assert isinstance(req, CueGenerationRequest)
        assert isinstance(ctx, PlannerMemoryContext)
        assert req.memory_id == ctx.memory_id


def test_load_demo_dataset_by_category_filters_correctly() -> None:
    social = load_demo_dataset_by_category("social")
    assert len(social) >= 1
    for req, ctx in social:
        spec = next(s for s in DEMO_MEMORIES if s.memory_id == req.memory_id)
        assert spec.category == "social"


def test_load_demo_dataset_by_category_unknown_returns_empty() -> None:
    assert load_demo_dataset_by_category("nonexistent-category") == []


def test_list_demo_memory_ids_returns_all_ids() -> None:
    ids = list_demo_memory_ids()
    assert len(ids) == len(DEMO_MEMORIES)
    assert all(mid.startswith("demo-") for mid in ids)


def test_list_demo_memory_specs_returns_all_specs() -> None:
    specs = list_demo_memory_specs()
    assert len(specs) == len(DEMO_MEMORIES)


# ---------------------------------------------------------------------------
# Dataset quality tests
# ---------------------------------------------------------------------------


def test_all_summaries_are_distinct() -> None:
    """No two memories should share an identical summary."""
    summaries = [m.summary for m in DEMO_MEMORIES]
    assert len(summaries) == len(set(summaries)), "duplicate summaries found in DEMO_MEMORIES"


def test_summaries_have_minimum_length() -> None:
    """Each summary should be substantive enough to give the planner material to work with."""
    for spec in DEMO_MEMORIES:
        assert len(spec.summary) >= 60, (
            f"Summary for '{spec.memory_id}' is too short ({len(spec.summary)} chars): {spec.summary!r}"
        )


def test_some_memories_have_multiple_images() -> None:
    """At least some memories should have 2+ image URIs to exercise multi-slide paths."""
    multi_image = [m for m in DEMO_MEMORIES if len(m.image_asset_uris) >= 2]
    assert len(multi_image) >= 2, (
        f"Expected at least 2 memories with multiple images, found {len(multi_image)}"
    )
