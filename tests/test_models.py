from remembra.cues.service import create_cue_variant, create_inference_run
from remembra.db.enums import (
    AssetType,
    CueTone,
    CueType,
    JobStatus,
    MemoryType,
    PersonalizationLevel,
)
from remembra.db.models import ScoreOutput
from remembra.db.schemas import (
    AssetCreate,
    CueVariantCreate,
    InferenceRunCreate,
    MemoryCreate,
    PersonCreate,
    PlaceCreate,
    ScoreOutputCreate,
)
from remembra.memory.service import (
    add_person_to_memory,
    create_asset,
    create_memory,
    create_person,
    create_place,
    get_memory,
)
from remembra.scoring.service import create_score_output


def test_model_creation_and_relationships(db_session) -> None:
    place = create_place(db_session, PlaceCreate(name="Library", description="Main campus library"))
    person = create_person(db_session, PersonCreate(full_name="Kai Rivera", notes=None))
    memory = create_memory(
        db_session,
        MemoryCreate(
            external_id="memory-001",
            title="Orientation Morning",
            narrative="Met classmates outside the library before opening session.",
            memory_type=MemoryType.EPISODIC,
            place_id=place.id,
        ),
    )
    add_person_to_memory(db_session, memory, person)
    create_asset(
        db_session,
        AssetCreate(
            memory_id=memory.id,
            asset_type=AssetType.IMAGE,
            uri="memory://asset/library-photo",
            description="Reference image",
        ),
    )

    cue_variant = create_cue_variant(
        db_session,
        CueVariantCreate(
            memory_id=memory.id,
            cue_type=CueType.TEXT_PROMPT,
            tone=CueTone.NEUTRAL,
            personalization_level=PersonalizationLevel.MEDIUM,
            prompt_text="Recall the conversation outside the library entrance.",
        ),
    )

    run = create_inference_run(
        db_session,
        InferenceRunCreate(cue_variant_id=cue_variant.id, status=JobStatus.PENDING),
    )

    create_score_output(
        db_session,
        ScoreOutputCreate(
            inference_run_id=run.id,
            metric_name="predicted_alignment",
            metric_value=0.42,
            details_json={"note": "placeholder"},
        ),
    )

    persisted_memory = get_memory(db_session, memory.id)

    assert persisted_memory is not None
    assert persisted_memory.place is not None
    assert persisted_memory.place.name == "Library"
    assert len(persisted_memory.people) == 1
    assert len(persisted_memory.assets) == 1
    assert len(persisted_memory.cue_variants) == 1

    persisted_score = db_session.query(ScoreOutput).one()
    assert persisted_score.metric_name == "predicted_alignment"
