from __future__ import annotations

from echomind.cues.contracts import CueDeliveryMode, CueMetadataKey
from echomind.cues.planner import (
    PlannerMemoryContext,
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.scoring.metrics import personalization_factor


# ---------------------------------------------------------------------------
# Structural / family tests
# ---------------------------------------------------------------------------


def test_planner_generates_expected_families_for_demo() -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context()

    variants = plan_deterministic_mvp_variants(request, context)

    families = [variant.metadata[CueMetadataKey.VARIANT_FAMILY.value] for variant in variants]
    assert families == [
        "text_generic",
        "text_autobiographical",
        "narration_neutral",
        "narration_warm",
        "slideshow_neutral",
        "slideshow_warm",
    ]

    for variant in variants:
        assert CueMetadataKey.SEED.value in variant.metadata
        assert CueMetadataKey.PLANNING_VERSION.value in variant.metadata


def test_planner_skips_slideshow_when_no_images() -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context().model_copy(update={"image_asset_uris": []})

    variants = plan_deterministic_mvp_variants(request, context)

    assert all(variant.delivery_mode != CueDeliveryMode.SLIDESHOW_NARRATION for variant in variants)
    assert len(variants) == 4


def test_planner_respects_context_flags() -> None:
    request = build_demo_planning_request().model_copy(
        update={
            "include_people_context": False,
            "include_place_context": False,
        }
    )
    context = build_demo_planner_context()

    variants = plan_deterministic_mvp_variants(request, context)

    assert variants
    for variant in variants:
        assert variant.metadata[CueMetadataKey.PEOPLE_USED.value] == []
        assert variant.metadata[CueMetadataKey.PLACE_USED.value] is None


def test_planner_is_deterministic_with_input_order_changes() -> None:
    request = build_demo_planning_request()
    context_a = PlannerMemoryContext(
        memory_id="demo-memory-001",
        memory_title="First Day at University",
        memory_summary="Walked across campus and located the first lecture hall with friends.",
        people_names=["Professor Lin", "Asha Patel"],
        place_name="New Brunswick Campus",
        image_asset_uris=[
            "s3://demo-assets/campus-path-2.jpg",
            "s3://demo-assets/campus-path-1.jpg",
        ],
    )
    context_b = PlannerMemoryContext(
        memory_id="demo-memory-001",
        memory_title="First Day at University",
        memory_summary="Walked across campus and located the first lecture hall with friends.",
        people_names=["Asha Patel", "Professor Lin"],
        place_name="New Brunswick Campus",
        image_asset_uris=[
            "s3://demo-assets/campus-path-1.jpg",
            "s3://demo-assets/campus-path-2.jpg",
        ],
    )

    variants_a = plan_deterministic_mvp_variants(request, context_a)
    variants_b = plan_deterministic_mvp_variants(request, context_b)

    assert [variant.model_dump(mode="json") for variant in variants_a] == [
        variant.model_dump(mode="json") for variant in variants_b
    ]


# ---------------------------------------------------------------------------
# Personalization factor — updated after generic metadata change
# ---------------------------------------------------------------------------


def test_personalization_factor_for_generic_is_baseline() -> None:
    """Generic cue has people_used=[] and place_used=None so factor should be exactly LOW (1.00)."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    text_generic = next(item for item in variants if item.cue_id.endswith("text-generic"))
    assert text_generic.metadata[CueMetadataKey.PEOPLE_USED.value] == []
    assert text_generic.metadata[CueMetadataKey.PLACE_USED.value] is None
    assert personalization_factor(text_generic) == 1.00


def test_personalization_factor_for_autobiographical_is_high() -> None:
    """Autobiographical cue has people and place context so factor should be HIGH + bonuses."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    text_autobio = next(item for item in variants if item.cue_id.endswith("text-autobiographical"))
    import pytest
    assert personalization_factor(text_autobio) == pytest.approx(1.14)


# ---------------------------------------------------------------------------
# Semantic separation: generic vs autobiographical (TEXT_ONLY)
# ---------------------------------------------------------------------------


def test_generic_cue_does_not_contain_people_names() -> None:
    """Generic text cue must not reference specific people by name."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    generic = next(v for v in variants if v.cue_id.endswith("text-generic"))
    for name in context.people_names:
        assert name not in generic.script_text, (
            f"Generic cue should not reference person '{name}'"
        )


def test_generic_cue_does_not_contain_place_name() -> None:
    """Generic text cue must not reference the specific place."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    generic = next(v for v in variants if v.cue_id.endswith("text-generic"))
    assert context.place_name not in generic.script_text, (
        f"Generic cue should not reference place '{context.place_name}'"
    )


def test_autobiographical_cue_contains_people_names() -> None:
    """Autobiographical text cue must reference at least one specific person."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    autobio = next(v for v in variants if v.cue_id.endswith("text-autobiographical"))
    assert any(name in autobio.script_text for name in context.people_names), (
        "Autobiographical cue should reference at least one person by name"
    )


def test_autobiographical_cue_contains_place_name() -> None:
    """Autobiographical text cue must reference the specific place."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    autobio = next(v for v in variants if v.cue_id.endswith("text-autobiographical"))
    assert context.place_name in autobio.script_text, (
        f"Autobiographical cue should reference place '{context.place_name}'"
    )


def test_generic_and_autobiographical_scripts_differ_substantially() -> None:
    """Generic and autobiographical scripts must differ by more than minor wording."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    generic = next(v for v in variants if v.cue_id.endswith("text-generic"))
    autobio = next(v for v in variants if v.cue_id.endswith("text-autobiographical"))

    assert generic.script_text != autobio.script_text
    # Check that they start with materially different phrases.
    assert generic.script_text[:20] != autobio.script_text[:20]
    # Autobiographical should be longer (it includes reconstruction framing).
    assert len(autobio.script_text) > len(generic.script_text)


# ---------------------------------------------------------------------------
# Semantic separation: warm vs neutral (NARRATION)
# ---------------------------------------------------------------------------


def test_neutral_narration_contains_factual_framing() -> None:
    """Neutral narration must read as a factual description, not an invitation."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    neutral_narration = next(
        v for v in variants
        if v.cue_id.endswith("narration-neutral")
    )
    assert "Recorded description:" in neutral_narration.script_text


def test_warm_narration_contains_invitation_language() -> None:
    """Warm narration must use invitational second-person framing."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    warm_narration = next(
        v for v in variants
        if v.cue_id.endswith("narration-warm")
    )
    assert "Take a moment" in warm_narration.script_text


def test_warm_and_neutral_narration_scripts_differ_materially() -> None:
    """Warm and neutral narration must differ beyond a single word or phrase."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    neutral = next(v for v in variants if v.cue_id.endswith("narration-neutral"))
    warm = next(v for v in variants if v.cue_id.endswith("narration-warm"))

    assert neutral.script_text != warm.script_text
    assert neutral.script_text[:30] != warm.script_text[:30]


# ---------------------------------------------------------------------------
# Slideshow image reference quality
# ---------------------------------------------------------------------------


def test_slideshow_slide_prompts_contain_uri_references() -> None:
    """Each slide_image_prompts entry must contain an extractable image URI."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    for variant in variants:
        if variant.delivery_mode != CueDeliveryMode.SLIDESHOW_NARRATION:
            continue
        for entry in variant.slide_image_prompts:
            has_uri = any(
                token.rstrip(".,;)]").startswith(("s3://", "memory://", "https://", "http://"))
                for token in entry.split()
            )
            assert has_uri, f"Slide entry missing URI: {entry!r}"


def test_slideshow_slide_prompts_include_slide_numbering() -> None:
    """Each slide entry should start with 'Slide N' for traceability."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    for variant in variants:
        if variant.delivery_mode != CueDeliveryMode.SLIDESHOW_NARRATION:
            continue
        for idx, entry in enumerate(variant.slide_image_prompts):
            assert entry.startswith(f"Slide {idx + 1}"), (
                f"Expected slide entry {idx} to start with 'Slide {idx + 1}', got: {entry!r}"
            )


def test_slideshow_narration_text_differs_from_plain_narration() -> None:
    """Slideshow narration should be distinct from the plain narration variant."""
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    narration_warm = next(v for v in variants if v.cue_id.endswith("narration-warm"))
    slideshow_warm = next(v for v in variants if v.cue_id.endswith("slideshow-warm"))

    assert narration_warm.narration_text != slideshow_warm.narration_text


def test_slideshow_without_images_is_skipped_not_errored() -> None:
    """When no images are available, slideshow variants should be omitted entirely."""
    request = build_demo_planning_request()
    context = build_demo_planner_context().model_copy(update={"image_asset_uris": []})
    variants = plan_deterministic_mvp_variants(request, context)

    slideshow_variants = [v for v in variants if v.delivery_mode == CueDeliveryMode.SLIDESHOW_NARRATION]
    assert slideshow_variants == []
