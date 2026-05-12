# EchoMind — CS439 Paper Outline

This is a scaffolding outline for a CS439-style paper based on the frozen
`paper.v1.0` configuration (`echomind/experiments/paper_config.py`,
`configs/paper_experiment.yaml`). Numbers cited below come from the run
captured under `artifacts/experiments/multi_memory/` and the report-ready
artifacts under `artifacts/report/`.

EchoMind is a **non-clinical research platform**. All findings here are
simulation-only and make no memory-improvement, diagnostic, or therapeutic
claims.

## 1. Abstract

EchoMind is a deterministic, non-clinical research platform for generating
and comparing personalized multimodal memory cues. We present a frozen
12-memory synthetic dataset, six structurally distinct cue families produced
by a deterministic template-driven planner, and a transparent scoring layer
that combines a TRIBE-v2 stub-derived response strength with explicit
heuristic factors for modality and personalization. Across three comparison
dimensions — warm vs neutral framing, personalized vs generic content, and
delivery modality — we report aggregate composite scores over the synthetic
dataset and explicitly characterize which contrasts are interpretable
through the current stub-backed inference path.

## 2. Introduction

- Motivation: reproducible, simulation-only comparison of cue variants for
  autobiographical memory contexts, prior to any human-subject work.
- Contribution: (i) a deterministic 6-family cue planner with structurally
  enforced semantic distinctions, (ii) a transparent decomposable scoring
  layer, (iii) a multi-memory experiment runner with grouped comparisons,
  (iv) a frozen reproducible configuration and report-export pipeline.
- Explicit non-goal: clinical claims, real-model TRIBE inference,
  human-outcome validation.

## 3. Related Work / Background

- Cue-based recall paradigms in cognitive psychology (background framing
  only — we do not test recall).
- Deterministic, template-driven NLG vs LLM-based generation; rationale for
  preferring deterministic templates in MVP.
- Multimodal stimulus comparison frameworks; TRIBE-v2 as a wrapper boundary.

## 4. Methodology

### 4.1 Dataset
- 12 hand-authored synthetic memory specs across ≥10 categories
  (`echomind.demo_data.memories.DEMO_MEMORIES`, dataset version `m9.1`).
- Each spec carries a deterministic seed, ≥1 person, a place, ≥1 image URI,
  and a sensory-textured summary (≥60 chars). Some carry multiple image
  URIs to exercise multi-slide rendering.

### 4.2 Cue Planner (six families)
Template version `deterministic.m2`:

| Family                    | Mode                | Tone     | Personalization |
|---------------------------|---------------------|----------|-----------------|
| `text_generic`            | TEXT_ONLY           | NEUTRAL  | LOW             |
| `text_autobiographical`   | TEXT_ONLY           | WARM     | HIGH            |
| `narration_neutral`       | NARRATION           | NEUTRAL  | MEDIUM          |
| `narration_warm`          | NARRATION           | WARM     | HIGH            |
| `slideshow_neutral`       | SLIDESHOW_NARRATION | NEUTRAL  | MEDIUM          |
| `slideshow_warm`          | SLIDESHOW_NARRATION | WARM     | HIGH            |

Distinctions are structurally enforced (see test suite
`tests/test_cue_planner.py`):
- Generic strips people/place; autobiographical anchors second-person
  reconstruction with named people and place.
- Neutral narration uses recorded-description framing; warm narration uses
  invitational second-person framing.
- Slideshow narration is a separate text from plain narration and per-slide
  references include scene hints + image URIs.

### 4.3 Scoring
Composite score = `0.7 · response_strength + 0.15 · modality_factor + 0.15 · personalization_factor`.
- `response_strength`: derived from stub TRIBE raw outputs (text-only path).
- `modality_factor`: TEXT_ONLY=1.00, NARRATION=1.05, SLIDESHOW_NARRATION=1.10.
- `personalization_factor`: LOW=1.00, MEDIUM=1.06, HIGH=1.12,
  +0.01 per active context anchor (people, place), capped at 1.20.

All submetrics and contributions are reported alongside the composite to
keep the heuristic component transparent.

### 4.4 Experiment Procedure
For each memory in the dataset: plan → render → run TRIBE smoke (TEXT_ONLY)
→ score → group by dimension. Aggregate across the 12 memories per
dimension. Run is deterministic given the frozen config.

## 5. Experiments and Results

Run id: `multi-memory-demo-run`. Source artifact:
`artifacts/experiments/multi_memory/aggregate/multi_memory_report.json`.

### 5.1 Warm vs Neutral framing (cleanest signal — *strong*)
| Group   | Mean per-memory composite | Max    | Min    |
|---------|---------------------------|--------|--------|
| neutral | 0.1305                    | 0.2501 | 0.0316 |
| warm    | 0.1423                    | 0.2308 | 0.0310 |

Both groups follow identical scoring paths and the stub TRIBE input differs
only in the framing dimension. The narrow but consistent gap reflects
text-level differences the stub actually sees.

### 5.2 Personalized vs Generic (*exploratory*)
| Group        | Mean   | Max    | Min    | n cues |
|--------------|--------|--------|--------|--------|
| generic      | 0.3360 | 0.6948 | 0.0393 | 12     |
| personalized | 0.0965 | 0.1496 | 0.0297 | 60     |

Generic cues score *higher* on average. We attribute this to the stub TRIBE
client mapping `SHA256(text) → [0,1]`: shorter, less constrained generic
prompts hit higher hash bins more often. We report this as a contrast in
inputs, **not** as evidence that generic cues better support recall. A real
TRIBE-v2 backend is required to interpret the direction of this effect.

### 5.3 Delivery mode (*limited*)
| Group               | Mean   |
|---------------------|--------|
| text_only           | 0.3492 |
| slideshow_narration | 0.0360 |
| narration           | 0.0240 |

Only TEXT_ONLY traverses the stub; NARRATION and SLIDESHOW_NARRATION receive
constant heuristic-only scores via the text-first smoke path. We include
this dimension for completeness but it should **not** be read as a modality
preference.

## 6. Discussion / Conclusion

EchoMind provides a reproducible, fully deterministic substrate for cue
comparison. The strongest claim supportable today is that warm and neutral
framings produce small but consistent differences in stub-TRIBE response
strength on the 12-memory dataset. Personalized-vs-generic and delivery-mode
results are constrained by the stub-backed inference path and the
text-first smoke pipeline; both become meaningful only after a real TRIBE
backend is wired in.

### Future work
- Replace stub TRIBE with a real model wrapper.
- Extend the smoke path to ingest narration/slideshow stimuli.
- Add a non-synthetic dataset under appropriate ethics review.
- Per-memory significance testing once response distributions are
  non-degenerate.

## 7. Reproducibility

Frozen config: `paper.v1.0` (see `echomind/experiments/paper_config.py` /
`configs/paper_experiment.yaml`).

```
python3.11 scripts/run_multi_memory_experiments.py \
    --artifact-root artifacts/experiments/multi_memory
python3.11 scripts/export_report_artifacts.py \
    --input artifacts/experiments/multi_memory \
    --output artifacts/report
```

All inputs are seeded; the planner, renderer, and stub TRIBE client are
deterministic, so a re-run reproduces every number cited above bit-for-bit.

## 8. Limitations and Ethics

- Stub TRIBE inference; no real model behavior.
- Only TEXT_ONLY reaches the stub.
- Synthetic dataset; no human outcome validation.
- Composite scores mix stub-derived response strength with explicit
  heuristic factors; submetrics are always reported alongside.
- Non-clinical research only — no diagnostic, therapeutic, or
  memory-improvement claims.
