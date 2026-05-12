"""Lightweight experiment runner for deterministic MVP comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from echomind.cues.contracts import CueDeliveryMode
from echomind.demo_data.loader import load_demo_dataset
from echomind.experiments.models import ExperimentComparisonReport, MultiMemoryExperimentReport
from echomind.experiments.reports import run_demo_experiment_comparison, run_multi_memory_experiment


@dataclass(slots=True)
class ExperimentConfig:
    """Minimal config for one deterministic experiment run."""

    experiment_id: str = "demo-experiment"
    artifact_root: str = "artifacts/experiments"
    supported_modalities: set[CueDeliveryMode] | None = None


@dataclass(slots=True)
class MultiMemoryExperimentConfig:
    """Config for a multi-memory experiment run across the demo dataset."""

    run_id: str = "multi-memory-demo-run"
    artifact_root: str = "artifacts/experiments/multi_memory"
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


class MultiMemoryExperimentRunner:
    """Run the deterministic pipeline across the full synthetic demo dataset."""

    def run(self, config: MultiMemoryExperimentConfig) -> MultiMemoryExperimentReport:
        """Run multi-memory experiment comparison and return aggregated report."""

        dataset = load_demo_dataset()
        return run_multi_memory_experiment(
            dataset=dataset,
            run_id=config.run_id,
            artifact_root=config.artifact_root,
            supported_modalities=config.supported_modalities,
        )
