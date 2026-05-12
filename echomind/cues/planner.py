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

    variants: list[CueVariantSpec] = []

    if CueDeliveryMode.TEXT_ONLY in request.target_modes:
        text_candidates = [
            _build_text_generic_variant(
                request=request,
                context=context,
            ),
            _build_text_autobiographical_variant(
                request=request,
                context=context,
                people_used=people_used,
                place_used=place_used,
            ),
        ]
        variants.extend(text_candidates[: request.max_variants_per_mode])

    if CueDeliveryMode.NARRATION in request.target_modes:
        narration_candidates = [
            _build_narration_variant(
                request=request,
                context=context,
                tone=CueTone.NEUTRAL,
                people_used=people_used,
                place_used=place_used,
            ),
            _build_narration_variant(
                request=request,
                context=context,
                tone=CueTone.WARM,
                people_used=people_used,
                place_used=place_used,
            ),
        ]
        variants.extend(narration_candidates[: request.max_variants_per_mode])

    if CueDeliveryMode.SLIDESHOW_NARRATION in request.target_modes and image_uris:
        slideshow_candidates = [
            _build_slideshow_variant(
                request=request,
                context=context,
                tone=CueTone.NEUTRAL,
                people_used=people_used,
                place_used=place_used,
                image_uris=image_uris,
            ),
            _build_slideshow_variant(
                request=request,
                context=context,
                tone=CueTone.WARM,
                people_used=people_used,
                place_used=place_used,
                image_uris=image_uris,
            ),
        ]
        variants.extend(slideshow_candidates[: request.max_variants_per_mode])

    return variants


# ---------------------------------------------------------------------------
# Internal builders
# ---------------------------------------------------------------------------


def _build_metadata(
    request: CueGenerationRequest,
    variant_family: str,
    people_used: list[str],
    place_used: str | None,
) -> dict[str, object]:
    return {
        CueMetadataKey.VARIANT_FAMILY.value: variant_family,
        CueMetadataKey.TEMPLATE_VERSION.value: "deterministic.m2",
        CueMetadataKey.SEED.value: request.seed,
        CueMetadataKey.PLANNING_VERSION.value: request.planning_version,
        CueMetadataKey.PEOPLE_USED.value: people_used,
        CueMetadataKey.PLACE_USED.value: place_used,
    }


def _build_text_generic_variant(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
) -> CueVariantSpec:
    """Generic text cue: impersonal, event-category level, no people or place context.

    This is the control condition — it describes the event type without anchoring
    to any specific individuals or location. Personalization metadata is explicitly
    zeroed so the scoring layer treats this as a context-free baseline.
    """
    script = (
        f"Event type: {context.memory_title}. "
        f"General description: {context.memory_summary} "
        f"This prompt describes the event in general terms, "
        f"without reference to specific people or locations involved."
    )

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
            people_used=[],
            place_used=None,
        ),
    )


def _build_text_autobiographical_variant(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
    people_used: list[str],
    place_used: str | None,
) -> CueVariantSpec:
    """Autobiographical text cue: explicit first-person reconstruction with named people and place.

    Substantially distinct from the generic variant — uses second-person active
    reconstruction framing, names specific people, and anchors the memory to a
    specific location.
    """
    place_line = f" You were at {place_used}." if place_used else ""
    people_line = (
        f" {', '.join(people_used)} {'was' if len(people_used) == 1 else 'were'} there with you."
        if people_used
        else ""
    )

    script = (
        f"Bring this memory back clearly. {context.memory_title}: "
        f"{context.memory_summary}"
        f"{place_line}{people_line}"
        f" Reconstruct it step by step — where you were standing, who was around you,"
        f" what you noticed first, and what happened next."
    )

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
    people_used: list[str],
    place_used: str | None,
) -> CueVariantSpec:
    personalization_level = (
        PersonalizationLevel.MEDIUM if tone == CueTone.NEUTRAL else PersonalizationLevel.HIGH
    )

    if tone == CueTone.NEUTRAL:
        script = _build_narration_neutral_script(context, people_used, place_used)
    else:
        script = _build_narration_warm_script(context, people_used, place_used)

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


def _build_narration_neutral_script(
    context: PlannerMemoryContext,
    people_used: list[str],
    place_used: str | None,
) -> str:
    """Factual, detached narration. Reads like a descriptive audio record."""
    place_line = f" Location: {place_used}." if place_used else ""
    people_line = (
        f" Participants: {', '.join(people_used)}." if people_used else ""
    )
    return (
        f"Recorded description: {context.memory_title}. "
        f"{context.memory_summary}"
        f"{place_line}{people_line}"
    )


def _build_narration_warm_script(
    context: PlannerMemoryContext,
    people_used: list[str],
    place_used: str | None,
) -> str:
    """Warm, second-person narration. Invites reconnection with the memory."""
    place_line = f" You were at {place_used}." if place_used else ""
    people_line = (
        f" You shared this with {', '.join(people_used)}." if people_used else ""
    )
    return (
        f"Take a moment to return to this memory. {context.memory_title} — "
        f"{context.memory_summary}"
        f"{place_line}{people_line}"
        f" Let yourself be there again, and notice what comes back."
    )


def _build_slideshow_variant(
    request: CueGenerationRequest,
    context: PlannerMemoryContext,
    tone: CueTone,
    people_used: list[str],
    place_used: str | None,
    image_uris: list[str],
) -> CueVariantSpec:
    selected_images = image_uris[:3]
    slide_refs = [
        _describe_slide(uri=uri, idx=i, memory_title=context.memory_title, place_name=place_used or "")
        for i, uri in enumerate(selected_images)
    ]

    if tone == CueTone.NEUTRAL:
        narration = _build_slideshow_neutral_script(context, people_used, place_used, selected_images)
    else:
        narration = _build_slideshow_warm_script(context, people_used, place_used, selected_images)

    return CueVariantSpec(
        cue_id=f"{request.memory_id}-slideshow-{tone.value}",
        memory_id=request.memory_id,
        delivery_mode=CueDeliveryMode.SLIDESHOW_NARRATION,
        tone=tone,
        personalization_level=PersonalizationLevel.HIGH,
        script_text=narration,
        narration_text=narration,
        slide_image_prompts=slide_refs,
        metadata=_build_metadata(
            request=request,
            variant_family=f"slideshow_{tone.value}",
            people_used=people_used,
            place_used=place_used,
        ),
    )


def _build_slideshow_neutral_script(
    context: PlannerMemoryContext,
    people_used: list[str],
    place_used: str | None,
    image_uris: list[str],
) -> str:
    """Factual slideshow narration describing the visual sequence objectively."""
    place_line = f" The images are set at {place_used}." if place_used else ""
    participants_line = (
        f" Participants shown: {', '.join(people_used)}." if people_used else ""
    )
    slide_count = len(image_uris)
    return (
        f"Visual memory record: {context.memory_title}. "
        f"{context.memory_summary}"
        f"{place_line}{participants_line}"
        f" This sequence contains {slide_count} image{'s' if slide_count != 1 else ''}."
    )


def _build_slideshow_warm_script(
    context: PlannerMemoryContext,
    people_used: list[str],
    place_used: str | None,
    image_uris: list[str],
) -> str:
    """Warm slideshow narration that invites the viewer to reconnect through the images."""
    place_line = f" These scenes are from {place_used}." if place_used else ""
    people_line = (
        f" Look for {', '.join(people_used)} in these moments." if people_used else ""
    )
    return (
        f"As each image appears, let it bring back {context.memory_title}. "
        f"{context.memory_summary}"
        f"{place_line}{people_line}"
        f" Watch these scenes and let the memory return."
    )


def _describe_slide(uri: str, idx: int, memory_title: str, place_name: str) -> str:
    """Build a descriptive slide reference entry containing the image URI.

    Format: "Slide N — <scene hint> at <place>: <uri>"

    The URI is always present so the renderer can extract it reliably.
    The scene hint is derived from the URI filename for traceability.
    """
    filename_hint = (
        uri.rstrip("/")
        .rsplit("/", 1)[-1]
        .removesuffix(".jpg")
        .removesuffix(".jpeg")
        .removesuffix(".png")
        .replace("-", " ")
        .replace("_", " ")
    )
    place_part = f" at {place_name}" if place_name else ""
    return f"Slide {idx + 1} — {filename_hint}{place_part}: {uri}"
