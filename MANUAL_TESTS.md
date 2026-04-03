# MANUAL_TESTS

This file is a living manual validation checklist for EchoMind.

EchoMind is non-clinical research software. All checks below validate simulation pipeline behavior only.

## How To Use This File
- Before a milestone: run the sections relevant to changed modules.
- After a milestone: update the “Most Recent Validation Pass” section with date and pass/fail notes.
- Keep failed checks listed with short context until fixed.

## Environment Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

## Database Setup And Seed
```bash
alembic upgrade head
python -m scripts.seed_demo_data
```

Expected:
- migration completes without errors
- demo memory graph is created (or seed exits safely if already present)

## API Smoke Checks
Run API:
```bash
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

Checks:
```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/memories
```

Expected:
- `/health` returns status `ok`
- `/memories` returns seeded memory records and related entities

## Planner Inspection Steps
```bash
python - <<'PY'
from echomind.cues.planner import build_demo_planning_request, build_demo_planner_context, plan_deterministic_mvp_variants
request = build_demo_planning_request()
context = build_demo_planner_context()
variants = plan_deterministic_mvp_variants(request, context)
print([v.metadata["variant_family"] for v in variants])
PY
```

Expected:
- six deterministic families:
  - `text_generic`
  - `text_autobiographical`
  - `narration_neutral`
  - `narration_warm`
  - `slideshow_neutral`
  - `slideshow_warm`

## Renderer Inspection Steps
```bash
python - <<'PY'
from echomind.media.renderer import render_demo_planner_outputs
manifest = render_demo_planner_outputs()
print(manifest.manifest_id, len(manifest.stimuli))
print([s.delivery_mode.value for s in manifest.stimuli])
PY
```

Expected:
- manifest is generated
- text, narration, and slideshow_narration stimuli are present
- deterministic artifact paths are written under `artifacts/media/`

## TRIBE Preprocess Inspection Steps
```bash
python - <<'PY'
from echomind.media.renderer import render_demo_planner_outputs
from echomind.tribe.preprocess import preprocess_manifest_for_tribe
manifest = render_demo_planner_outputs()
batch = preprocess_manifest_for_tribe(manifest=manifest, request_id="manual-preprocess")
print([item.modality.value for item in batch.stimuli])
PY
```

Expected:
- current smoke configuration filters to `text_only` inputs for reliability

## Text-Only Smoke Inference Steps
```bash
python - <<'PY'
from echomind.tribe.infer import run_demo_text_only_smoke_inference
result = run_demo_text_only_smoke_inference()
print(result.summary.status.value)
print(result.summary.ranked_cue_ids[:3])
print(result.artifacts.run_dir)
PY
```

Expected:
- inference status is `succeeded`
- ranked cue ids are present
- artifacts are persisted deterministically

## Scoring And Experiment Comparison Steps
```bash
python -m scripts.run_demo_comparison
```

Expected:
- deterministic comparison report is generated
- report includes decomposed submetrics and composite ranking
- grouped summaries are produced for:
  - personalized vs generic
  - warm vs neutral
  - delivery mode

## Artifact Files That Should Exist
- `artifacts/media/<memory_id>/<cue_id>/...`
- `artifacts/inference/tribe/<request_id>/request.json`
- `artifacts/inference/tribe/<request_id>/raw_outputs.json`
- `artifacts/inference/tribe/<request_id>/summary.json`
- `artifacts/inference/tribe/<request_id>/metadata.json`
- `artifacts/experiments/reports/<experiment_id>/comparison_report.json`

## Most Recent Validation Pass
- Date: 2026-04-03
- Passed:
  - API smoke (`/health`, `/memories`)
  - deterministic cue planning output families
  - deterministic renderer artifacts for text/narration/slideshow_narration
  - TRIBE preprocess text-only filter for smoke path
  - text-only smoke inference success with saved request/raw/summary/metadata artifacts
  - scoring + experiment comparison report generation path
- Notes:
  - TRIBE execution remains stub-backed for local deterministic runs.
  - Multimodal TRIBE execution beyond text-first smoke path is not yet validated.

## Recommended Edge Cases For Later
- cues with no image assets (slideshow variants should be skipped cleanly)
- cues missing narration text (renderer should fail explicitly)
- non-text modality preprocessing when TRIBE adapter support is expanded
- scoring behavior when raw outputs are missing and aggregate fallback is used
- cross-run comparison reproducibility under changed scoring weights
