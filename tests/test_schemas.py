from remembra.cues.service import create_cue_variant
from remembra.db.enums import AssetType, CueTone, CueType, MemoryType, PersonalizationLevel
from remembra.db.schemas import AssetCreate, CueVariantCreate, MemoryCreate, MemoryRead, PlaceCreate
from remembra.memory.service import create_asset, create_memory, create_place


def test_memory_schema_serialization(db_session) -> None:
    place = create_place(db_session, PlaceCreate(name="Student Center", description=None))
    memory = create_memory(
        db_session,
        MemoryCreate(
            external_id="memory-serialize-001",
            title="Campus Meetup",
            narrative="Met peers at the student center.",
            memory_type=MemoryType.EPISODIC,
            place_id=place.id,
        ),
    )
    create_asset(
        db_session,
        AssetCreate(
            memory_id=memory.id,
            asset_type=AssetType.TEXT,
            uri="memory://asset/note",
            description="Text memo",
        ),
    )
    create_cue_variant(
        db_session,
        CueVariantCreate(
            memory_id=memory.id,
            cue_type=CueType.TEXT_PROMPT,
            tone=CueTone.WARM,
            personalization_level=PersonalizationLevel.LOW,
            prompt_text="Recall the meetup at the student center.",
        ),
    )

    db_session.refresh(memory)
    serialized = MemoryRead.model_validate(memory)

    assert serialized.external_id == "memory-serialize-001"
    assert serialized.memory_type == MemoryType.EPISODIC
    assert serialized.place is not None
    assert serialized.place.name == "Student Center"
    assert len(serialized.assets) == 1
    assert len(serialized.cue_variants) == 1
