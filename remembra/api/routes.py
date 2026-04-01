"""API route definitions."""

from fastapi import APIRouter

from remembra.core.utils import utc_now_iso
from remembra.memory.service import load_demo_memory

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Service liveness endpoint."""

    return {"status": "ok", "timestamp_utc": utc_now_iso()}


@router.get("/memory/demo")
def demo_memory() -> dict[str, str]:
    """Return a single demo memory artifact for MVP testing."""

    record = load_demo_memory()
    return {
        "memory_id": record.memory_id,
        "title": record.title,
        "narrative": record.narrative,
    }
