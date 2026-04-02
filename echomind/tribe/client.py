"""TRIBE wrapper interfaces and placeholder client."""

from dataclasses import dataclass


@dataclass(slots=True)
class TribeSimulationResult:
    """Simulation output placeholder for predicted cortical response."""

    cue_id: str
    response_score: float


class TribeClient:
    """Placeholder TRIBE wrapper; implementation added in later phases."""

    def simulate(self, cue_id: str) -> TribeSimulationResult:
        """Run in-silico simulation for one cue candidate."""

        # TODO: Replace with real TRIBE integration behind this boundary.
        return TribeSimulationResult(cue_id=cue_id, response_score=0.0)
