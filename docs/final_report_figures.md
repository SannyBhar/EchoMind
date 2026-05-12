# Final Report Figures

This note maps the publication-ready CS439 figure and table artifacts produced by
`scripts/export_report_artifacts.py` to suggested paper placement.

All results are non-clinical and simulation-only. The frozen slice is
`paper.v1.0`, using the deterministic 12-memory dataset and the text-first
TRIBE smoke path.

## Regeneration

```bash
./.venv/bin/python scripts/run_multi_memory_experiments.py \
    --artifact-root artifacts/experiments/multi_memory
./.venv/bin/python scripts/export_report_artifacts.py \
    --input artifacts/experiments/multi_memory \
    --output artifacts/report
```

## Figures

### `artifacts/report/final_figures/figure_1_pipeline_overview.png`

- Shows:
  planner -> renderer -> text-first TRIBE smoke path -> scoring -> grouped comparisons/reporting
- Suggested placement:
  Methodology overview, near §4.4 of [docs/paper_outline.md](/Users/sankeerthbharadwaj/Desktop/Tribe%20Projects/EchoMind/docs/paper_outline.md)
- Suggested caption:
  "EchoMind frozen publication pipeline. Cue variants are planned deterministically, rendered into local artifacts, passed through a text-first TRIBE smoke path, scored with decomposed submetrics, and aggregated into grouped comparison outputs."
- Caveat:
  State that only `TEXT_ONLY` cues currently traverse the TRIBE stub.

### `artifacts/report/final_figures/figure_2_grouped_composite_scores.png`

- Shows:
  Mean per-memory composite score for all three comparison dimensions in one grouped figure
- Suggested placement:
  Results section opener before dimension-specific subsections
- Suggested caption:
  "Grouped average composite scores across the three comparison dimensions in the frozen 12-memory run. Confidence labels indicate which dimensions are strongest versus most constrained by the current simulation path."
- Caveat:
  Mention that delivery-mode values are not directly comparable to a real multimodal inference result because only `TEXT_ONLY` reaches the stub.

### `artifacts/report/final_figures/figure_3_personalized_vs_generic.png`

- Shows:
  Per-memory personalized vs generic comparison across all 12 synthetic memories
- Suggested placement:
  §5.2 Personalized vs Generic
- Suggested caption:
  "Per-memory average composite score for generic and personalized cue groups. The direction in this frozen run is driven by deterministic stub-text variance and should be interpreted as an input contrast, not a recall-quality claim."
- Caveat:
  Explicitly state that the generic advantage is a stub artifact tied to the SHA256-based placeholder inference path.

### `artifacts/report/final_figures/figure_4_warm_vs_neutral.png`

- Shows:
  Warm vs neutral mean per-memory composite score with ±1 SD error bars
- Suggested placement:
  §5.1 Warm vs Neutral framing
- Suggested caption:
  "Warm versus neutral framing in the frozen 12-memory run. Bars show mean per-memory composite score and error bars show ±1 SD across memories."
- Caveat:
  This is the cleanest current contrast, but it is still simulation-only and not a human recall outcome.

### `artifacts/report/final_figures/figure_5_delivery_mode_limited.png`

- Shows:
  Mean per-memory composite score by delivery mode (`text_only`, `narration`, `slideshow_narration`)
- Suggested placement:
  §5.3 Delivery Mode
- Suggested caption:
  "Delivery-mode comparison under the current text-first smoke path. `TEXT_ONLY` traverses the TRIBE stub, while narration and slideshow values are heuristic-only constants."
- Caveat:
  The paper must visibly state that this figure is limited by the current smoke path and is not evidence of modality preference.

## Figure Companion CSVs

These are saved under `artifacts/report/final_figures/data/`.

- `figure_2_grouped_composite_scores.csv`
  Mean/min/max and cue counts for the grouped comparison figure
- `figure_3_personalized_vs_generic.csv`
  Per-memory generic and personalized averages plus the gap
- `figure_4_warm_vs_neutral.csv`
  Warm/neutral summary statistics used for the error-bar figure
- `figure_5_delivery_mode_limited.csv`
  Delivery-mode summary statistics used for the limited comparison figure

## Table Artifacts

### `artifacts/report/final_tables/table_1_representative_ranked_cues.csv`

- Shows:
  Ranked cue family breakdown for the representative memory (`demo-university-001`)
- Suggested placement:
  Example walk-through in Results or Appendix
- Caveat:
  Keep the decomposed submetrics visible; do not cite the composite alone.

### `artifacts/report/final_tables/table_1_representative_ranked_cues.md`

- Markdown rendering of the same representative ranked-cue table

### `artifacts/report/final_tables/table_2_summary_findings.csv`

- Shows:
  One-row-per-dimension summary with interpretation label, confidence, and limitation note
- Suggested placement:
  Discussion summary or Appendix

### `artifacts/report/final_tables/table_2_summary_findings.md`

- Markdown rendering of the same summary findings table

## Paper Caveats To Preserve

- EchoMind is non-clinical, simulation-only research software.
- `response_strength` is stub-derived in this frozen slice.
- `modality_factor` and `personalization_factor` are explicit heuristics.
- Delivery-mode results are limited because only `TEXT_ONLY` traverses the TRIBE stub.
- Personalized vs generic directionality in this run is not evidence that generic cues are preferable.
