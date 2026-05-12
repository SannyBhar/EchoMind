# Report Artifacts

This document maps the report-ready artifacts produced by
`scripts/export_report_artifacts.py` to the sections of `paper_outline.md`.

## How to regenerate

```
python3.11 scripts/run_multi_memory_experiments.py \
    --artifact-root artifacts/experiments/multi_memory
python3.11 scripts/export_report_artifacts.py \
    --input  artifacts/experiments/multi_memory \
    --output artifacts/report
```

The export script is deterministic given the frozen `paper.v1.0` config.

## Artifact inventory

All paths are relative to `artifacts/report/` unless noted.

| Artifact | Description | Used in paper section |
|---|---|---|
| `summary.json` | Frozen paper config + aggregate comparisons + run metadata. | §4 (Methodology), §7 (Reproducibility) |
| `dimension_summary.csv` | One row per (dimension, group) with mean / max / min per-memory composite scores. | §5.1, §5.2, §5.3 |
| `per_memory_scores.csv` | Flat table: every ranked cue across all 12 memories, with submetrics and family. | §5 supporting data; appendix |
| `representative_memory_ranked.csv` | Ranked cues for `demo-university-001` (illustrative single-memory ranking). | §5 example walk-through |
| `representative_memory_meta.json` | Memory id and title for the representative example. | §5 caption |
| `plots/dimension_warm_vs_neutral.png` | Mean composite per group for warm vs neutral. | §5.1 |
| `plots/dimension_personalized_vs_generic.png` | Mean composite per group for personalized vs generic. | §5.2 |
| `plots/dimension_delivery_mode.png` | Mean composite per delivery mode (carries an in-figure caveat about stub limits). | §5.3 |
| `plots/per_memory_personalized_vs_generic.png` | Per-memory side-by-side bars (with caveat caption). | §5.2 |
| `plots/representative_memory_ranked.png` | Horizontal bar chart of one memory's ranked cues. | §5 example |

## Confidence labeling (matches `paper_config.PAPER_DIMENSIONS`)

- **strong** — `warm_vs_neutral`. Same scoring path; stub-TRIBE input
  actually differs in the studied dimension.
- **exploratory** — `personalized_vs_generic`. Direction is confounded by
  stub-text variance; report as input contrast, not as a recall claim.
- **limited** — `delivery_mode`. Narration/slideshow are heuristic-only
  constants under the text-first smoke path.

## Honest framing checklist (use when drafting captions)

- Always cite the composite *and* its three submetrics — never the composite
  alone.
- For the delivery-mode plot, retain the in-figure note that
  narration/slideshow scores are constants from the smoke path.
- For personalized-vs-generic, do not claim generic cues are "better";
  describe the magnitude as a stub-text artifact pending a real TRIBE
  backend.
- Cite the run id (`multi-memory-demo-run`) and the frozen config version
  (`paper.v1.0`) in any figure or table caption that quotes a number.
