from echomind.cues.contracts import CueDeliveryMode, CueMetadataKey
from echomind.cues.planner import (
    PlannerMemoryContext,
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)


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
