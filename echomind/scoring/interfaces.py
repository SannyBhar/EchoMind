"""Scoring interface placeholders."""

from typing import Protocol


class CueScorer(Protocol):
    """Contract for decomposable, interpretable cue scoring."""

    def score(self, cue_id: str, simulation_artifact: dict[str, float]) -> dict[str, float]:
        """Return named score components for transparent ranking."""
