from sqlalchemy import select

from remembra.db.models import Asset, CueVariant, Memory, Person, Place
from scripts.seed_demo_data import seed_demo_data


def test_seed_script_inserts_demo_graph(db_session) -> None:
    seed_demo_data(db_session)

    memory = db_session.scalar(select(Memory).where(Memory.external_id == "demo-memory-001"))
    people = db_session.scalars(select(Person)).all()
    places = db_session.scalars(select(Place)).all()
    assets = db_session.scalars(select(Asset)).all()
    variants = db_session.scalars(select(CueVariant)).all()

    assert memory is not None
    assert len(people) == 2
    assert len(places) == 1
    assert 2 <= len(assets) <= 3
    assert len(variants) == 2


def test_seed_script_is_idempotent(db_session) -> None:
    seed_demo_data(db_session)
    seed_demo_data(db_session)

    memories = db_session.scalars(select(Memory)).all()
    assert len(memories) == 1
