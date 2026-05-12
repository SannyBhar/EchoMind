"""Demo dataset loader: builds (CueGenerationRequest, PlannerMemoryContext) pairs
from the synthetic DemoMemorySpec definitions.
"""

from __future__ import annotations

from echomind.cues.contracts import CueDeliveryMode, CueGenerationRequest
from echomind.cues.planner import PlannerMemoryContext
from echomind.demo_data.memories import DEMO_MEMORIES, DemoMemorySpec

_DEFAULT_TARGET_MODES = [
    CueDeliveryMode.TEXT_ONLY,
    CueDeliveryMode.NARRATION,
    CueDeliveryMode.SLIDESHOW_NARRATION,
]


def build_context_from_spec(spec: DemoMemorySpec) -> PlannerMemoryContext:
    """Build a PlannerMemoryContext from a DemoMemorySpec."""
    return PlannerMemoryContext(
        memory_id=spec.memory_id,
        memory_title=spec.title,
        memory_summary=spec.summary,
        people_names=list(spec.people_names),
        place_name=spec.place_name,
        image_asset_uris=list(spec.image_asset_uris),
    )


def build_request_from_spec(spec: DemoMemorySpec) -> CueGenerationRequest:
    """Build a CueGenerationRequest from a DemoMemorySpec."""
    return CueGenerationRequest(
        request_id=f"plan-{spec.memory_id}",
        memory_id=spec.memory_id,
        memory_title=spec.title,
        memory_summary=spec.summary,
        target_modes=_DEFAULT_TARGET_MODES,
        max_variants_per_mode=2,
        include_people_context=True,
        include_place_context=True,
        seed=spec.seed,
        planning_version="mvp.v1",
    )


def load_demo_dataset() -> list[tuple[CueGenerationRequest, PlannerMemoryContext]]:
    """Return (request, context) pairs for all synthetic demo memories."""
    return [
        (build_request_from_spec(spec), build_context_from_spec(spec))
        for spec in DEMO_MEMORIES
    ]


def load_demo_dataset_by_category(
    category: str,
) -> list[tuple[CueGenerationRequest, PlannerMemoryContext]]:
    """Return (request, context) pairs filtered to one category."""
    return [
        (build_request_from_spec(spec), build_context_from_spec(spec))
        for spec in DEMO_MEMORIES
        if spec.category == category
    ]


def list_demo_memory_ids() -> list[str]:
    """Return memory_ids for all synthetic demo memories."""
    return [spec.memory_id for spec in DEMO_MEMORIES]


def list_demo_memory_specs() -> list[DemoMemorySpec]:
    """Return all DemoMemorySpec definitions."""
    return list(DEMO_MEMORIES)
