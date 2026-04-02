"""Experiment runner placeholders."""

from dataclasses import dataclass


@dataclass(slots=True)
class ExperimentConfig:
    """Minimal experiment configuration placeholder."""

    experiment_id: str
    description: str


class ExperimentRunner:
    """Placeholder experiment orchestrator."""

    def run(self, config: ExperimentConfig) -> dict[str, str]:
        """Run a placeholder experiment flow and return status metadata."""

        return {"experiment_id": config.experiment_id, "status": "not_implemented"}
