"""Cue generation interface placeholders."""

from typing import Protocol


class CuePlanner(Protocol):
    """Contract for deterministic cue-variant planning."""

    def plan(self, memory_id: str) -> list[dict[str, str]]:
        """Return schema-ready cue plan artifacts for a memory."""
