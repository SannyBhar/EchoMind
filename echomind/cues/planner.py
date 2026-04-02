"""Deterministic MVP cue planner for EchoMind."""

from __future__ import annotations

from pydantic import BaseModel, Field

from echomind.cues.contracts import (
    CueDeliveryMode,
    CueGenerationRequest,
    CueMetadataKey,
    CueVariantSpec,
)
from echomind.db.enums import CueTone, PersonalizationLevel


class PlannerMemoryContext(BaseModel):
    """Lightweight planning context detached from rendering/inference layers."""

    memory_id: str
    memory_title: str
    memory_summary: str
    people_names: list[str] = Field(default_factory=list)
    place_name: str | None = None
    image_asset_uris: list[str] = Field(default_factory=list)


def build_demo_planning_request() -> CueGenerationRequest:
    """Return a deterministic demo planning request aligned to seed data."""

    return CueGenerationRequest(
        request_id="plan-demo-memory-001",
        memory_id="demo-memory-001",
        memory_title="First Day at University",
        memory_summary="Walked across campus and located the first lecture hall with friends.",
        target_modes=[
            CueDeliveryMode.TEXT_ONLY,
            CueDeliveryMode.NARRATION,
            CueDeliveryMode.SLIDESHOW_NARRATION,
        ],
        max_variants_per_mode=2,
        include_people_context=True,
        include_place_context=True,
        seed=7,
        planning_version="mvp.v1",
    )


def build_demo_planner_context() -> PlannerMemoryContext:
    """Return a lightweight demo context matching seeded memory entities."""

    return PlannerMemoryContext(
        memory_id="demo-memory-001",
        memory_title="First Day at University",
        memory_summary="Walked across campus and located the first lecture hall with friends.",
        people_names=["Asha Patel", "Professor Lin"],
        place_name="New Brunswick Campus",
        image_asset_uris=["s3://demo-assets/campus-path.jpg"],
    )


def plan_deterministic_mvp_variants(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
) -> list[CueVariantSpec]:
    """Build deterministic cue variants for MVP research comparisons."""

    # Keep behavior deterministic regardless of input order.
    people_names = sorted({name.strip() for name in context.people_names if name.strip()})
    image_uris = sorted({uri.strip() for uri in context.image_asset_uris if uri.strip()})

    people_used = people_names if request.include_people_context else []
    place_used = context.place_name if request.include_place_context else None

    personalization_clause = _build_personalization_clause(
        people_used=people_used,
        place_used=place_used,
    )

    variants: list[CueVariantSpec] = []

    if CueDeliveryMode.TEXT_ONLY in request.target_modes:
        text_generic = _build_text_generic_variant(
            request=request,
            context=context,
            personalization_clause=personalization_clause,
            people_used=people_used,
            place_used=place_used,
        )
        text_candidates = [
            text_generic,
            _build_text_autobiographical_variant(
                request,
                context,
                personalization_clause,
                people_used,
                place_used,
            ),
        ]
        variants.extend(text_candidates[: request.max_variants_per_mode])

    if CueDeliveryMode.NARRATION in request.target_modes:
        narration_candidates = [
            _build_narration_variant(
                request,
                context,
                tone=CueTone.NEUTRAL,
                personalization_clause=personalization_clause,
                people_used=people_used,
                place_used=place_used,
            ),
            _build_narration_variant(
                request,
                context,
                tone=CueTone.WARM,
                personalization_clause=personalization_clause,
                people_used=people_used,
                place_used=place_used,
            ),
        ]
        variants.extend(narration_candidates[: request.max_variants_per_mode])

    if CueDeliveryMode.SLIDESHOW_NARRATION in request.target_modes and image_uris:
        slideshow_candidates = [
            _build_slideshow_variant(
                request,
                context,
                tone=CueTone.NEUTRAL,
                personalization_clause=personalization_clause,
                people_used=people_used,
                place_used=place_used,
                image_uris=image_uris,
            ),
            _build_slideshow_variant(
                request,
                context,
                tone=CueTone.WARM,
                personalization_clause=personalization_clause,
                people_used=people_used,
                place_used=place_used,
                image_uris=image_uris,
            ),
        ]
        variants.extend(slideshow_candidates[: request.max_variants_per_mode])

    return variants


def _build_metadata(
    request: CueGenerationRequest,
    variant_family: str,
    people_used: list[str],
    place_used: str | None,
) -> dict[str, object]:
    return {
        CueMetadataKey.VARIANT_FAMILY.value: variant_family,
        CueMetadataKey.TEMPLATE_VERSION.value: "deterministic.m1",
        CueMetadataKey.SEED.value: request.seed,
        CueMetadataKey.PLANNING_VERSION.value: request.planning_version,
        CueMetadataKey.PEOPLE_USED.value: people_used,
        CueMetadataKey.PLACE_USED.value: place_used,
    }


def _build_personalization_clause(people_used: list[str], place_used: str | None) -> str:
    parts: list[str] = []
    if people_used:
        parts.append(f"People context: {', '.join(people_used)}.")
    if place_used:
        parts.append(f"Place context: {place_used}.")
    return " ".join(parts)


def _build_text_generic_variant(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
    personalization_clause: str,
    people_used: list[str],
    place_used: str | None,
) -> CueVariantSpec:
    script = (
        f"Recall this moment: {context.memory_title}. "
        f"Summary: {context.memory_summary}."
    )
    if personalization_clause:
        script = f"{script} {personalization_clause}"

    return CueVariantSpec(
        cue_id=f"{request.memory_id}-text-generic",
        memory_id=request.memory_id,
        delivery_mode=CueDeliveryMode.TEXT_ONLY,
        tone=CueTone.NEUTRAL,
        personalization_level=PersonalizationLevel.LOW,
        script_text=script,
        metadata=_build_metadata(
            request=request,
            variant_family="text_generic",
            people_used=people_used,
            place_used=place_used,
        ),
    )


def _build_text_autobiographical_variant(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
    personalization_clause: str,
    people_used: list[str],
    place_used: str | None,
) -> CueVariantSpec:
    script = (
        f"Think through the event '{context.memory_title}' in first person. "
        f"Reconstruct what happened step-by-step from this summary: {context.memory_summary}."
    )
    if personalization_clause:
        script = f"{script} {personalization_clause}"

    return CueVariantSpec(
        cue_id=f"{request.memory_id}-text-autobiographical",
        memory_id=request.memory_id,
        delivery_mode=CueDeliveryMode.TEXT_ONLY,
        tone=CueTone.WARM,
        personalization_level=PersonalizationLevel.HIGH,
        script_text=script,
        metadata=_build_metadata(
            request=request,
            variant_family="text_autobiographical",
            people_used=people_used,
            place_used=place_used,
        ),
    )


def _build_narration_variant(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
    tone: CueTone,
    personalization_clause: str,
    people_used: list[str],
    place_used: str | None,
) -> CueVariantSpec:
    script = (
        f"Narration cue ({tone.value}): {context.memory_title}. "
        f"Summary: {context.memory_summary}."
    )
    if personalization_clause:
        script = f"{script} {personalization_clause}"

    personalization_level = (
        PersonalizationLevel.MEDIUM if tone == CueTone.NEUTRAL else PersonalizationLevel.HIGH
    )

    return CueVariantSpec(
        cue_id=f"{request.memory_id}-narration-{tone.value}",
        memory_id=request.memory_id,
        delivery_mode=CueDeliveryMode.NARRATION,
        tone=tone,
        personalization_level=personalization_level,
        script_text=script,
        narration_text=script,
        metadata=_build_metadata(
            request=request,
            variant_family=f"narration_{tone.value}",
            people_used=people_used,
            place_used=place_used,
        ),
    )


def _build_slideshow_variant(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
    tone: CueTone,
    personalization_clause: str,
    people_used: list[str],
    place_used: str | None,
    image_uris: list[str],
) -> CueVariantSpec:
    selected_images = image_uris[:3]
    slide_prompts = [f"Use reference image: {uri}" for uri in selected_images]

    narration = (
        f"Slideshow narration ({tone.value}) for {context.memory_title}. "
        f"Summary: {context.memory_summary}."
    )
    if personalization_clause:
        narration = f"{narration} {personalization_clause}"

    return CueVariantSpec(
        cue_id=f"{request.memory_id}-slideshow-{tone.value}",
        memory_id=request.memory_id,
        delivery_mode=CueDeliveryMode.SLIDESHOW_NARRATION,
        tone=tone,
        personalization_level=PersonalizationLevel.HIGH,
        script_text=narration,
        narration_text=narration,
        slide_image_prompts=slide_prompts,
        metadata=_build_metadata(
            request=request,
            variant_family=f"slideshow_{tone.value}",
            people_used=people_used,
            place_used=place_used,
        ),
    )
