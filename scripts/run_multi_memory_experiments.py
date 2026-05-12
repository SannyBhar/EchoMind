#!/usr/bin/env python
"""Run the EchoMind multi-memory experiment pipeline across the synthetic demo dataset.

Executes the deterministic flow (plan -> render -> TRIBE smoke -> score -> compare)
for all 12 synthetic demo memories and writes experiment-ready output artifacts.

Outputs:
  artifacts/experiments/multi_memory/per_memory/<memory_id>/  — per-memory artifacts
  artifacts/experiments/multi_memory/aggregate/multi_memory_report.json
  artifacts/experiments/multi_memory/aggregate/dimension_summary.csv

Usage:
  python scripts/run_multi_memory_experiments.py
  python scripts/run_multi_memory_experiments.py --artifact-root /path/to/artifacts
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from echomind.demo_data.loader import load_demo_dataset
from echomind.experiments.reports import run_multi_memory_experiment


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run EchoMind multi-memory experiments")
    parser.add_argument(
        "--artifact-root",
        default="artifacts/experiments/multi_memory",
        help="Root directory for output artifacts (default: artifacts/experiments/multi_memory)",
    )
    parser.add_argument(
        "--run-id",
        default="multi-memory-demo-run",
        help="Identifier for this experiment run (default: multi-memory-demo-run)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    artifact_root = Path(args.artifact_root)

    dataset = load_demo_dataset()
    print(f"EchoMind multi-memory experiment: {len(dataset)} synthetic demo memories")
    print(f"Artifact root: {artifact_root.resolve()}")
    print()

    report = run_multi_memory_experiment(
        dataset=dataset,
        run_id=args.run_id,
        artifact_root=artifact_root,
    )

    print(f"Completed: {report.memory_count} memories processed")
    print()
    print("=== Aggregated Dimension Summaries ===")
    for dim in report.aggregated_comparisons:
        print(f"\n  {dim.dimension}:")
        for grp in dim.groups:
            print(
                f"    {grp.group_key:30s}  "
                f"mean={grp.mean_avg_composite_score:.4f}  "
                f"max={grp.max_avg_composite_score:.4f}  "
                f"min={grp.min_avg_composite_score:.4f}  "
                f"memories={grp.memory_count}  cues={grp.total_cues}"
            )

    agg_dir = artifact_root / "aggregate"
    print()
    print(f"Aggregate JSON : {agg_dir / 'multi_memory_report.json'}")
    print(f"Dimension CSV  : {agg_dir / 'dimension_summary.csv'}")
    print()
    print("Note: TRIBE execution uses the deterministic stub client.")
    print("Modality and personalization factors are explicit simulation heuristics.")


if __name__ == "__main__":
    main(sys.argv[1:])
