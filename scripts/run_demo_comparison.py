"""Run deterministic demo scoring and experiment comparison for EchoMind."""

from __future__ import annotations

from echomind.experiments.reports import run_demo_experiment_comparison


def main() -> None:
    report = run_demo_experiment_comparison()
    print(
        "Generated experiment comparison:",
        report.experiment_id,
        f"top cue={report.metadata.get('top_cue_id')}",
        f"score={report.metadata.get('top_composite_score')}",
    )


if __name__ == "__main__":
    main()
