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
- `echomind/scoring`: score persistence service and scoring interface placeholders

### Current Data Flow
1. Memory context is loaded from persisted entities (`Memory`, `Person`, `Place`, `Asset`).
2. Deterministic cue planner produces `CueVariantSpec` families.
3. Media renderer converts cue variants into local artifacts + validated `RenderedStimulus`.
4. `RenderedStimulus` items are grouped into `StimulusManifest`.
5. TRIBE preprocess layer maps stimuli to `TribeBatchInput` (text-first smoke path currently).
6. TRIBE client wrapper runs batch inference (stub by default) and emits raw outputs.
7. Raw outputs + summary + run metadata are persisted to deterministic local artifact paths.
8. Future scoring layer will consume persisted inference outputs.

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
- Scoring boundary (future): inference outputs -> score summaries + persistence

## Architecture Decisions
1. Deterministic planning before LLM generation:
- baseline reproducibility and testability are required before adding stochastic generation.

2. Rendering before TRIBE integration:
- TRIBE inputs depend on stable, validated stimulus artifacts and manifests.

3. Text-first TRIBE smoke path before multimodal expansion:
- enables a reliable end-to-end path while keeping modality expansion isolated in preprocess/adapters.

4. Non-clinical framing is enforced system-wide:
- design, docs, and service behavior avoid diagnostic/treatment claims.

## Known Extensions
- replace stub TRIBE client with environment-backed real client implementation
- expand preprocess support for narration/slideshow modalities
- add interpretable scoring computation over simulation outputs
- add experiment orchestration and richer dashboard result views
