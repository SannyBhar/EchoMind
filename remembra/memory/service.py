"""Memory-domain persistence services."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from remembra.db.models import Asset, Memory, Person, Place
from remembra.db.schemas import AssetCreate, MemoryCreate, PersonCreate, PlaceCreate


@dataclass(slots=True)
class DemoMemoryRecord:
    """Fallback demo memory for shell bootstrapping without DB dependency."""

    memory_id: str
    title: str
    narrative: str


def load_demo_memory() -> DemoMemoryRecord:
    """Return one in-silico demo memory record for shell rendering."""

    return DemoMemoryRecord(
        memory_id="demo-memory-001",
        title="First Day at University",
        narrative="A non-clinical sample autobiographical memory for in-silico cue comparison.",
    )


def create_place(session: Session, payload: PlaceCreate) -> Place:
    """Create and persist a place record."""

    place = Place(**payload.model_dump())
    session.add(place)
    session.flush()
    return place


def create_person(session: Session, payload: PersonCreate) -> Person:
    """Create and persist a person record."""

    person = Person(**payload.model_dump())
    session.add(person)
    session.flush()
    return person


def create_memory(session: Session, payload: MemoryCreate) -> Memory:
    """Create and persist a memory record."""

    memory = Memory(**payload.model_dump())
    session.add(memory)
    session.flush()
    return memory


def create_asset(session: Session, payload: AssetCreate) -> Asset:
    """Create and persist an asset record."""

    asset = Asset(**payload.model_dump())
    session.add(asset)
    session.flush()
    return asset


def add_person_to_memory(session: Session, memory: Memory, person: Person) -> Memory:
    """Associate a person with a memory."""

    if person not in memory.people:
        memory.people.append(person)
        session.flush()
    return memory


def list_memories(session: Session) -> list[Memory]:
    """List memories with related entities needed for API serialization."""

    stmt = (
        select(Memory)
        .options(
            selectinload(Memory.place),
            selectinload(Memory.people),
            selectinload(Memory.assets),
            selectinload(Memory.cue_variants),
        )
        .order_by(Memory.id)
    )
    return list(session.scalars(stmt).all())


def get_memory(session: Session, memory_id: int) -> Memory | None:
    """Fetch one memory by numeric identifier with related entities."""

    stmt = (
        select(Memory)
        .where(Memory.id == memory_id)
        .options(
            selectinload(Memory.place),
            selectinload(Memory.people),
            selectinload(Memory.assets),
            selectinload(Memory.cue_variants),
        )
    )
    return session.scalar(stmt)


def get_memory_by_external_id(session: Session, external_id: str) -> Memory | None:
    """Fetch a memory by stable external identifier."""

    stmt = select(Memory).where(Memory.external_id == external_id)
    return session.scalar(stmt)
