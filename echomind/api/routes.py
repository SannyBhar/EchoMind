"""API route definitions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from echomind.api.dependencies import db_session_dependency
from echomind.core.utils import utc_now_iso
from echomind.db.schemas import MemoryRead
from echomind.memory.service import get_memory, list_memories, load_demo_memory

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Service liveness endpoint."""

    return {"status": "ok", "timestamp_utc": utc_now_iso()}


@router.get("/memories", response_model=list[MemoryRead])
def read_memories(session: Session = Depends(db_session_dependency)) -> list[MemoryRead]:
    """List stored memories with minimal related entities."""

    memories = list_memories(session)
    return [MemoryRead.model_validate(memory) for memory in memories]


@router.get("/memories/{memory_id}", response_model=MemoryRead)
def read_memory(memory_id: int, session: Session = Depends(db_session_dependency)) -> MemoryRead:
    """Read one memory and its related entities."""

    memory = get_memory(session, memory_id=memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryRead.model_validate(memory)


@router.get("/memory/demo")
def demo_memory() -> dict[str, str]:
    """Return a static demo memory placeholder for bootstrapping."""

    record = load_demo_memory()
    return {
        "memory_id": record.memory_id,
        "title": record.title,
        "narrative": record.narrative,
    }
