"""Lightweight experiment runner for deterministic MVP comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from echomind.cues.contracts import CueDeliveryMode
from echomind.experiments.models import ExperimentComparisonReport
from echomind.experiments.reports import run_demo_experiment_comparison


@dataclass(slots=True)
class ExperimentConfig:
    """Minimal config for one deterministic experiment run."""

    experiment_id: str = "demo-experiment"
    artifact_root: str = "artifacts/experiments"
    supported_modalities: set[CueDeliveryMode] | None = None


class ExperimentRunner:
    """Run a deterministic experiment comparison flow for MVP evaluation."""

    def run(self, config: ExperimentConfig) -> ExperimentComparisonReport:
        """Run demo-memory experiment comparison and return structured report."""

        report = run_demo_experiment_comparison(
            artifact_root=Path(config.artifact_root) / config.experiment_id,
            supported_modalities=config.supported_modalities,
        )
        report.experiment_id = config.experiment_id
        return report
