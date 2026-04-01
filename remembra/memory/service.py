"""Memory domain service interfaces."""

from dataclasses import dataclass


@dataclass(slots=True)
class DemoMemoryRecord:
    """Minimal demo autobiographical memory placeholder."""

    memory_id: str
    title: str
    narrative: str


def load_demo_memory() -> DemoMemoryRecord:
    """Return one demo memory record for MVP bootstrapping."""

    return DemoMemoryRecord(
        memory_id="demo-memory-001",
        title="First Day at University",
        narrative="A non-clinical sample autobiographical memory for in-silico cue comparison.",
    )
