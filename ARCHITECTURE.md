# ARCHITECTURE

## Current Architecture (Repo Truth)

### Major Modules
- `apps/api`: FastAPI app and routes
- `apps/dashboard`: Streamlit shell
- `apps/worker`: Celery worker entrypoint
- `echomind/core`: settings, logging, shared utilities
- `echomind/db`: SQLAlchemy models, schemas, sessions, enums
- `echomind/memory`: memory and related entity services
- `echomind/cues`: cue contracts, deterministic planner, cue persistence service
- `echomind/media`: rendering contracts, deterministic renderer, swappable adapters (TTS/slideshow)
- `echomind/tribe`: preprocessing, wrapper client, inference orchestration, aggregates, artifact persistence
- `echomind/scoring`: explicit metrics, weighted composite assembly, explanation helpers, scoring pipeline
- `echomind/experiments`: grouped comparison outputs, report assembly, deterministic demo comparison runner

### Current Data Flow
1. Memory context is loaded from persisted entities (`Memory`, `Person`, `Place`, `Asset`).
2. Deterministic cue planner produces `CueVariantSpec` families.
3. Media renderer converts cue variants into local artifacts + validated `RenderedStimulus`.
4. `RenderedStimulus` items are grouped into `StimulusManifest`.
5. TRIBE preprocess layer maps stimuli to `TribeBatchInput` (text-first smoke path currently).
6. TRIBE client wrapper runs batch inference (stub by default) and emits raw outputs.
7. Raw outputs + summary + run metadata are persisted to deterministic local artifact paths.
8. Scoring layer computes response_strength + heuristic modality/personalization factors + composite score.
9. Experiment layer groups ranked cues by personalization, tone, and delivery mode for comparison views.

## Persistence Layer
- SQLAlchemy 2.0 models for memory/cue/inference/score entities
- Alembic migration baseline in `migrations/`
- seed script for deterministic demo data in `scripts/seed_demo_data.py`
- local deterministic artifact trees for media and inference outputs

## Service Roles
- API: health + memory read endpoints for seeded and persisted entities
- Dashboard: placeholder non-clinical inspection shell
- Worker: placeholder Celery task path

## Contract Boundaries
- Planner boundary: `CueGenerationRequest` -> `CueVariantSpec`
- Renderer boundary: `CueVariantSpec` -> `RenderedStimulus` / `StimulusManifest`
- Inference boundary: `StimulusManifest` -> `TribeBatchInput` -> raw outputs + `InferenceResultSummary`
- Scoring boundary: inference outputs + cue metadata -> decomposable cue scores
- Experiment boundary: scored cues -> grouped experiment comparison report

## Architecture Decisions
1. Deterministic planning before LLM generation:
- baseline reproducibility and testability are required before adding stochastic generation.

2. Rendering before TRIBE integration:
- TRIBE inputs depend on stable, validated stimulus artifacts and manifests.

3. Text-first TRIBE smoke path before multimodal expansion:
- enables a reliable end-to-end path while keeping modality expansion isolated in preprocess/adapters.

4. Non-clinical framing is enforced system-wide:
- design, docs, and service behavior avoid diagnostic/treatment claims.

5. Heuristic factors are explicit and separated from model-derived signals:
- modality and personalization contributions are labeled as heuristic metadata factors.

## Known Extensions
- replace stub TRIBE client with environment-backed real client implementation
- expand preprocess support for narration/slideshow modalities
- persist scoring outputs to DB-linked score records at run time
- add richer dashboard result views and product-facing comparison APIs
