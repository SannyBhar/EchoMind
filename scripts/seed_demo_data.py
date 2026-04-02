"""Seed minimal non-clinical demo data for MVP development."""

from __future__ import annotations

from sqlalchemy.orm import Session

from echomind.cues.service import create_cue_variant
from echomind.db.enums import AssetType, CueTone, CueType, MemoryType, PersonalizationLevel
from echomind.db.schemas import (
    AssetCreate,
    CueVariantCreate,
    MemoryCreate,
    PersonCreate,
    PlaceCreate,
)
from echomind.db.session import SessionLocal, session_scope
from echomind.memory.service import (
    add_person_to_memory,
    create_asset,
    create_memory,
    create_person,
    create_place,
    get_memory_by_external_id,
)


def seed_demo_data(session: Session) -> None:
    """Insert one deterministic demo graph for MVP experimentation."""

    existing_memory = get_memory_by_external_id(session, "demo-memory-001")
    if existing_memory is not None:
        return

    place = create_place(
        session,
        PlaceCreate(
            name="New Brunswick Campus", description="University campus context for demo memory"
        ),
    )

    person_one = create_person(
        session,
        PersonCreate(full_name="Asha Patel", notes="Close friend present in the memory context."),
    )
    person_two = create_person(
        session,
        PersonCreate(full_name="Professor Lin", notes="Mentor figure in the memory context."),
    )

    memory = create_memory(
        session,
        MemoryCreate(
            external_id="demo-memory-001",
            title="First Day at University",
            narrative=(
                "Walked across campus with friends, located the first lecture hall, "
                "and felt grounded."
            ),
            memory_type=MemoryType.EPISODIC,
            place_id=place.id,
        ),
    )

    add_person_to_memory(session, memory, person_one)
    add_person_to_memory(session, memory, person_two)

    create_asset(
        session,
        AssetCreate(
            memory_id=memory.id,
            asset_type=AssetType.IMAGE,
            uri="s3://demo-assets/campus-path.jpg",
            description="Campus walkway image used as a candidate cue source.",
        ),
    )
    create_asset(
        session,
        AssetCreate(
            memory_id=memory.id,
            asset_type=AssetType.AUDIO,
            uri="s3://demo-assets/campus-ambience.wav",
            description="Ambient campus audio used for simulation-based cue testing.",
        ),
    )
    create_asset(
        session,
        AssetCreate(
            memory_id=memory.id,
            asset_type=AssetType.TEXT,
            uri="memory://demo-memory-001/context-note",
            description="Short textual context note attached to the memory.",
        ),
    )

    create_cue_variant(
        session,
        CueVariantCreate(
            memory_id=memory.id,
            cue_type=CueType.TEXT_PROMPT,
            tone=CueTone.NEUTRAL,
            personalization_level=PersonalizationLevel.MEDIUM,
            prompt_text=(
                "Recall the path to your first lecture hall and the people you noticed around you."
            ),
        ),
    )
    create_cue_variant(
        session,
        CueVariantCreate(
            memory_id=memory.id,
            cue_type=CueType.AUDIO_PROMPT,
            tone=CueTone.WARM,
            personalization_level=PersonalizationLevel.HIGH,
            prompt_text=(
                "Listen to campus ambience and reconstruct the moment you found your classroom."
            ),
        ),
    )


def main() -> None:
    """Run seed script against configured database."""

    with session_scope(SessionLocal) as session:
        seed_demo_data(session)


if __name__ == "__main__":
    main()
