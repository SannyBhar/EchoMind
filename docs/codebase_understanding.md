# EchoMind Codebase Understanding

## Purpose

This document explains how EchoMind works today for a new engineer joining the project.
It focuses on the implemented pipeline, the current abstraction boundaries, which parts are real versus simulated, and where future work can be added safely.

EchoMind is consistently framed in code as non-clinical, simulation-only research software. The core implemented slice is:

`planner -> renderer -> text-first TRIBE smoke path -> scoring -> experiment comparison -> dashboard/report inspection`

## Workflow Map

- Persisted demo memory path:
  `scripts/seed_demo_data.py` seeds one DB memory graph (`demo-memory-001`) with people, place, assets, and two cue variants.
- Synthetic experiment path:
  `echomind/demo_data/memories.py` defines 12 synthetic memories used by the planner and experiments without requiring the DB.
- Cue planning path:
  `CueGenerationRequest + PlannerMemoryContext -> plan_deterministic_mvp_variants() -> 6 CueVariantSpec outputs`
- Rendering path:
  `CueVariantSpec -> DeterministicMediaRenderer -> RenderedStimulus artifacts + StimulusManifest`
- TRIBE path:
  `StimulusManifest -> preprocess_manifest_for_tribe() -> TribeBatchInput -> StubTribeClient -> raw outputs + summary + persisted artifacts`
- Scoring path:
  `CueVariantSpec + TRIBE outputs -> score_cue_variants() -> ScoreBreakdown list + ScoringReport`
- Experiment path:
  `ScoringReport -> grouped comparisons + ranked cues -> per-memory and multi-memory reports -> optional report exports`
- Dashboard path:
  `run_demo_inspection()` reruns the deterministic demo pipeline, then renders tables, JSON, artifact previews, and grouped summaries in Streamlit.

## Part A: Repository Map

### Top-level structure

- `apps/`
  Runtime entrypoints.
- `echomind/`
  Main application and domain code.
- `migrations/`
  Alembic migration environment and the initial schema migration.
- `scripts/`
  Operational scripts for seeding, running experiments, and exporting report artifacts.
- `tests/`
  Unit/integration-style tests over planner, renderer, scoring, experiments, API, dashboard helpers, and demo dataset structure.
- `configs/`
  Present but currently not meaningfully used by the implemented pipeline.
- `docs/`
  Supporting documents for ethics, architecture, paper/report artifacts, and roadmap.
- `artifacts/`
  Generated local outputs from media rendering, inference runs, experiments, and report export.

### Major folders

#### `apps/`

- `apps/api/main.py`
  Real FastAPI entrypoint.
- `apps/dashboard/app.py`
  Real Streamlit dashboard entrypoint.
- `apps/worker/main.py`
  Real Celery worker entrypoint, but only for a ping task today.

These are the real service bootstraps, not helpers.

#### `echomind/`

This is the actual product code.

- `api/`
  Route wiring and dependencies for FastAPI.
- `core/`
  Settings, logging, utility helpers, Celery app construction.
- `db/`
  SQLAlchemy base/session, enums, ORM models, Pydantic schemas.
- `memory/`
  Persistence services for memories, people, places, assets, plus a simple fallback demo memory.
- `demo_data/`
  The synthetic 12-memory dataset used by the deterministic planner/experiment pipeline.
- `cues/`
  Cue contracts, the real deterministic planner, DB persistence helpers, and an older placeholder contract service.
- `media/`
  Deterministic renderer and adapter boundaries for TTS/slideshow rendering.
- `tribe/`
  Preprocess layer, client boundary, inference orchestration, aggregates, and artifact persistence.
- `scoring/`
  Explicit submetrics, composite scoring, explanations, and scoring pipeline.
- `experiments/`
  Grouped comparisons, per-memory and multi-memory orchestration, and paper/report configuration.
- `dashboard/`
  Thin service layer and view-model helpers used by Streamlit.

#### `migrations/`

- `migrations/versions/20260401_0001_initial_domain_models.py`
  Initial schema for memories, people, places, assets, cue variants, inference runs, and score outputs.

#### `scripts/`

- `seed_demo_data.py`
  Seeds one persisted demo memory graph into the DB.
- `run_demo_comparison.py`
  Runs the single-memory deterministic experiment path.
- `run_multi_memory_experiments.py`
  Runs the 12-memory synthetic experiment pipeline.
- `export_report_artifacts.py`
  Exports CSV/JSON/plot artifacts from a multi-memory run.

These are helper operational entrypoints, but they exercise the real pipeline.

#### `tests/`

Tests are organized by subsystem, mostly as focused unit/integration checks over deterministic functions and artifact writing.

#### `configs/`

Currently a placeholder for future config-driven work. The implemented code does not use this directory as its main source of truth yet.

#### `docs/`

- `docs/architecture.md`
  Older stub document.
- `ARCHITECTURE.md`
  More accurate current architecture summary.
- `MANUAL_TESTS.md`
  Best current statement of manually validated behaviors.
- `docs/report_artifacts.md`
  Maps exported report files to paper usage.

### Real runtime entrypoints vs helper code

Real runtime entrypoints:

- `apps/api/main.py`
- `apps/dashboard/app.py`
- `apps/worker/main.py`
- `scripts/seed_demo_data.py`
- `scripts/run_demo_comparison.py`
- `scripts/run_multi_memory_experiments.py`
- `scripts/export_report_artifacts.py`

Helper/composition code:

- Most of `echomind/*`
- `tests/*`
- `migrations/*`

## Part B: Current System Workflows

### 1. Memory/data workflow

#### Data model

The persisted domain model lives in `echomind/db/models/entities.py`.

- `Memory`
  Core autobiographical record with `external_id`, `title`, `narrative`, `memory_type`, optional `event_date`, optional `place`, many `people`, many `assets`, many `cue_variants`.
- `Person`
  Related people linked through `memory_people`.
- `Place`
  Optional location.
- `Asset`
  Source media references linked to a memory.
- `CueVariant`
  Persisted cue candidate with `cue_type`, `tone`, `personalization_level`, and `prompt_text`.
- `InferenceRun`
  Per-cue simulation execution metadata.
- `ScoreOutput`
  Persisted named score component for an inference run.

#### Important distinction: persisted DB model vs active experiment model

The implemented experiment pipeline does not currently operate from the DB model. It mostly uses:

- `DemoMemorySpec` in `echomind/demo_data/memories.py`
- `PlannerMemoryContext` in `echomind/cues/planner.py`
- `CueGenerationRequest` in `echomind/cues/contracts.py`

So there are two parallel “memory sources”:

- DB-seeded single demo memory for API/dashboard read paths
- Synthetic in-memory 12-memory dataset for experiments

#### Demo/synthetic memory data

Current source of truth for multi-memory experiments:

- `echomind/demo_data/memories.py`

It defines 12 synthetic `DemoMemorySpec` records with:

- `memory_id`
- `title`
- `summary`
- `people_names`
- `place_name`
- `image_asset_uris`
- `category`
- `seed`

Loader helpers in `echomind/demo_data/loader.py` convert each spec into:

- `PlannerMemoryContext`
- `CueGenerationRequest`

#### Persisted demo seed

`scripts/seed_demo_data.py` inserts one DB-backed memory graph with:

- one memory: `demo-memory-001`
- two people
- one place
- three assets
- two persisted cue variants

This is not the same dataset as the 12-memory synthetic experiment set.

#### Key limitation

The DB is not the current source of truth for the implemented experiment pipeline. The synthetic memory specs are.

### 2. Cue generation workflow

#### Flow

`CueGenerationRequest + PlannerMemoryContext -> plan_deterministic_mvp_variants()`

Core entrypoint:

- `echomind/cues/planner.py::plan_deterministic_mvp_variants`

The planner:

1. Normalizes/sorts people names and image URIs for deterministic behavior.
2. Applies include/exclude flags from `CueGenerationRequest`.
3. Generates up to two variants per delivery mode.
4. Returns a list of `CueVariantSpec`.

#### Six cue families

The implemented planner produces exactly six families when all three modes are enabled and image assets exist:

- `text_generic`
- `text_autobiographical`
- `narration_neutral`
- `narration_warm`
- `slideshow_neutral`
- `slideshow_warm`

#### Family behavior

- `text_generic`
  Control-style, low-personalization baseline with people/place metadata explicitly zeroed.
- `text_autobiographical`
  High-personalization text cue with named people and place.
- `narration_neutral`
  Factual descriptive narration.
- `narration_warm`
  Invitational/second-person narration.
- `slideshow_neutral`
  Factual slideshow narration over referenced images.
- `slideshow_warm`
  Warm slideshow narration over referenced images.

#### Metadata attached

Planner metadata is important because later stages use it for traceability and scoring:

- `variant_family`
- `template_version`
- `seed`
- `planning_version`
- `people_used`
- `place_used`

Why it matters:

- preserves auditability
- supports personalization scoring heuristics
- exposes planner provenance to renderer, dashboard, and reports

#### Core planner entrypoints

- `plan_deterministic_mvp_variants`
- `build_demo_planning_request`
- `build_demo_planner_context`

#### Key limitation

There is also an older placeholder planner path in `echomind/cues/contracts_service.py`. It is not the main implemented planner and should not be treated as the primary extension point.

### 3. Media rendering workflow

#### Flow

`CueVariantSpec -> DeterministicMediaRenderer.render_variant()/render_manifest() -> RenderedStimulus + StimulusManifest`

Core implementation:

- `echomind/media/renderer.py`

#### How modalities differ

Text:

- writes `text_prompt.txt`
- returns `RenderedStimulus(text_payload=...)`

Narration:

- requires `narration_text`
- writes `narration_script.txt`
- calls `TTSAdapter.synthesize()`
- writes `narration.wav`
- returns transcript + audio URI

Slideshow narration:

- requires `narration_text`
- extracts image URIs from `slide_image_prompts`
- writes `slideshow_narration_script.txt`
- synthesizes `slideshow_narration.wav`
- calls slideshow adapter
- writes `slideshow_plan.json` and `slideshow.mp4`
- returns transcript + audio URI + slide image URIs

#### Real vs stub-backed

Real:

- artifact directory creation
- manifest construction
- validation of cue/render shapes
- file writing
- image URI extraction logic

Stub-backed:

- TTS generation: `StubTTSAdapter` writes text payloads into `.wav` placeholder files
- slideshow rendering: `StubSlideshowRenderer` writes a JSON plan and a text placeholder `.mp4`

#### Artifact path layout

Path logic lives in `echomind/media/manifests.py`.

Artifacts are written under:

- `<artifact_root>/<sanitized_memory_id>/<sanitized_cue_id>/...`

The default root is usually `artifacts/media` or a workflow-specific subdirectory.

#### Key limitation

Media rendering is structurally real but content generation is not real audiovisual rendering yet.

### 4. TRIBE workflow

#### Flow

`StimulusManifest -> preprocess_manifest_for_tribe() -> TribeBatchInput -> TribeClient.infer_batch() -> build_inference_summary() -> save_tribe_run_artifacts()`

Core files:

- `echomind/tribe/preprocess.py`
- `echomind/tribe/client.py`
- `echomind/tribe/infer.py`
- `echomind/tribe/aggregates.py`
- `echomind/tribe/io.py`

#### Preprocessing

`preprocess_manifest_for_tribe()` converts `RenderedStimulus` objects into `TribeStimulusInput`.

Current behavior:

- default supported modalities: `{text_only}`
- narration and slideshow are filtered out unless explicitly enabled
- all supported modalities are normalized to a `text_input`

Text normalization today:

- text cue -> `text_payload`
- narration cue -> `narration_transcript`
- slideshow cue -> `narration_transcript`

So even the future multimodal expansion is currently text-normalized at the preprocess boundary.

#### Smoke path support

The current smoke path only truly supports `TEXT_ONLY`.

This is explicitly enforced in:

- `MANUAL_TESTS.md`
- `run_demo_text_only_smoke_inference()`
- `paper_config.py`

#### Client boundary

`TribeClient` is the intended adapter boundary.

Today’s implementation:

- `StubTribeClient`

It hashes `text_input` with SHA256, converts part of the digest into a deterministic `response_score`, and emits a small `response_vector`.

#### Saved outputs

Artifacts are written by `save_tribe_run_artifacts()` under:

- `artifacts/inference/tribe/<request_id>/request.json`
- `raw_outputs.json`
- `summary.json`
- `metadata.json`

#### Real vs simulated

Real:

- preprocessing
- batch input construction
- artifact persistence
- summary/ranking assembly

Simulated:

- actual TRIBE inference
- response scores
- response vectors

Text-normalized:

- all currently supported inputs passed to the stub client

### 5. Scoring workflow

#### Flow

`CueVariantSpec + InferenceResultSummary + TribeRawOutput[] -> score_cue_variants() -> ScoringReport`

Core files:

- `echomind/scoring/metrics.py`
- `echomind/scoring/composite.py`
- `echomind/scoring/explain.py`
- `echomind/scoring/pipeline.py`

#### Inputs used

Per cue:

- cue metadata and delivery mode from `CueVariantSpec`
- response scores from `TribeRawOutput` if present
- fallback aggregate scores from `InferenceResultSummary`

#### Metric definitions

`response_strength`

- model-derived in intent
- actually stub-derived today
- averages matching raw outputs for a cue
- falls back to `aggregate_scores[cue_id]`

`modality_factor`

- explicit heuristic
- values:
  - `text_only = 1.00`
  - `narration = 1.05`
  - `slideshow_narration = 1.10`

`personalization_factor`

- explicit heuristic
- base by personalization level:
  - `low = 1.00`
  - `medium = 1.06`
  - `high = 1.12`
- bonus:
  - `+0.01` if `people_used` exists
  - `+0.01` if `place_used` exists
- capped at `1.20`

`composite_score`

- weighted combination of:
  - `response_strength`
  - delta from 1.0 for `modality_factor`
  - delta from 1.0 for `personalization_factor`
- default weights:
  - response: `0.7`
  - modality: `0.15`
  - personalization: `0.15`

#### Explanations

Human-readable explanations are created in `build_score_explanation()`.
They identify the top contribution and print the three metric values.

#### Heuristic vs model-derived

Stub/model-derived:

- `response_strength`

Heuristic:

- `modality_factor`
- `personalization_factor`

Transparent design choice:

- heuristic factors are kept explicit and separate from the model-derived path

### 6. Experiment workflow

#### Single-memory comparison

Core path:

- `run_demo_experiment_comparison()`
- `run_memory_experiment()`

Steps:

1. plan variants
2. render media
3. run TRIBE smoke inference
4. score variants
5. rank cues
6. build grouped comparisons
7. save comparison report JSON

#### Grouped comparisons

Implemented dimensions:

- `personalized_vs_generic`
- `warm_vs_neutral`
- `delivery_mode`

Grouping logic lives in `echomind/experiments/compare.py`.

#### Multi-memory run

Core path:

- `run_multi_memory_experiment()`

It:

1. loads all `(request, context)` pairs from `load_demo_dataset()`
2. runs the full per-memory pipeline for each memory
3. saves per-memory reports
4. aggregates dimension summaries across memories
5. writes:
   - `aggregate/multi_memory_report.json`
   - `aggregate/dimension_summary.csv`

#### Aggregation

Cross-memory aggregation lives in `echomind/experiments/aggregate.py`.

It computes, per dimension/group:

- memory count
- total cues
- mean of per-memory average composite scores
- max/min of per-memory average composite scores

#### Report export

`scripts/export_report_artifacts.py` reads a completed multi-memory run and exports:

- `summary.json`
- `dimension_summary.csv`
- `per_memory_scores.csv`
- `representative_memory_ranked.csv`
- `representative_memory_meta.json`
- plots under `artifacts/report/plots`

It uses the frozen `paper.v1.0` configuration from `echomind/experiments/paper_config.py`.

#### Key limitation

The experiment framework is real orchestration over deterministic components, but the inference engine and several resulting comparisons are constrained by the text-first stub path.

### 7. Dashboard workflow

#### Data source

The Streamlit dashboard is not primarily reading precomputed reports from storage. It reruns the deterministic demo pipeline through `run_demo_inspection()`.

Core files:

- `apps/dashboard/app.py`
- `echomind/dashboard/service.py`
- `echomind/dashboard/view_models.py`

#### Service/view-model usage

Service layer:

- `run_demo_inspection()`
- `load_seeded_memory_overview()`
- `collect_stimulus_artifact_previews()`

View models:

- `cue_variant_rows()`
- `rendered_stimulus_rows()`
- `score_rows()`
- `group_rows()`

#### What is real vs derived

Reflects the real current pipeline:

- planner outputs
- rendered artifacts
- TRIBE request/summary/raw artifact paths
- scoring breakdowns
- grouped experiment summaries

Derived or fallback behavior:

- seeded memory overview falls back to planner context if DB access fails
- dashboard is an inspection surface, not a separate persisted application state

## Part C: Dependency and Extension-Point Analysis

### Most important modules/functions

- `echomind/cues/planner.py::plan_deterministic_mvp_variants`
- `echomind/media/renderer.py::DeterministicMediaRenderer`
- `echomind/tribe/preprocess.py::preprocess_manifest_for_tribe`
- `echomind/tribe/client.py::TribeClient`
- `echomind/tribe/infer.py::run_tribe_inference`
- `echomind/scoring/pipeline.py::score_cue_variants`
- `echomind/experiments/reports.py::{run_memory_experiment, run_multi_memory_experiment}`
- `echomind/demo_data/memories.py::DEMO_MEMORIES`
- `echomind/dashboard/service.py::run_demo_inspection`
- `echomind/db/models/entities.py`

### Safe extension points

#### Better cue generation

Safest places:

- `echomind/cues/planner.py`
- `echomind/cues/contracts.py`
- `echomind/demo_data/loader.py`

Why:

- planner is already isolated from rendering and inference
- metadata contract is explicit
- deterministic planning can be evolved without touching UI or TRIBE code

#### Richer scoring

Safest places:

- `echomind/scoring/metrics.py`
- `echomind/scoring/models.py`
- `echomind/scoring/pipeline.py`
- eventually config-backed weights in `configs/`

Why:

- scoring inputs and outputs are already decomposed
- explanation path is explicit
- heuristics are clearly separated from response-derived signals

#### Future product APIs

Safest places:

- `echomind/api/routes.py`
- a future service layer between `memory/`, `experiments/`, and `api/`
- the existing Pydantic schemas/contracts

Why:

- API is currently thin and easy to extend
- current business logic is mostly not tied to FastAPI internals

#### Eventual memory experience packaging

Safest places:

- `echomind/media/renderer.py`
- `echomind/media/interfaces.py`
- `echomind/media/{tts,slideshow}.py`
- `echomind/cues/contracts.py`

Why:

- cue specs and rendered stimuli already form a packaging boundary
- adapters can be swapped without changing planner/scoring code

#### Future AR-ready abstraction layers

Safest places:

- `CueVariantSpec`
- `RenderedStimulus`
- `StimulusManifest`
- media adapter interfaces

Why:

- these are modality/package abstractions
- they can evolve toward richer delivery bundles without entangling the TRIBE or dashboard layers

### Modules that should not be tightly coupled to future UI/AR work

- `echomind/scoring/*`
- `echomind/tribe/*`
- `echomind/demo_data/*`
- `echomind/experiments/*`
- `echomind/db/models/entities.py`

Reason:

- these are domain/pipeline layers, not presentation layers
- coupling them to UI or AR packaging would collapse current clean boundaries

## Part D: Validation Status

### Manually validated

Per `MANUAL_TESTS.md`, the repository claims a validation pass on 2026-04-03 for:

- API smoke
- deterministic cue family generation
- renderer artifact generation
- TRIBE preprocess text-only filtering
- text-only smoke inference artifact persistence
- scoring and experiment comparison generation

### Automated coverage present in tests

Covered by tests on disk:

- API health and memory endpoints
- SQLAlchemy models/schemas
- demo dataset structure and invariants
- cue contract validation
- deterministic planner outputs
- renderer outputs and slideshow failure behavior
- TRIBE preprocess and artifact persistence
- scoring functions and ranking
- experiment grouping and multi-memory aggregation
- dashboard helper/service shell behavior
- seed script behavior

### Stubbed or simulated

- TRIBE inference itself is stubbed
- narration audio is stubbed
- slideshow/video rendering is stubbed
- delivery-mode comparison is partly heuristic-only because non-text cues do not traverse the current smoke path
- DB-backed cue generation/inference/scoring runtime persistence is not the main active pipeline

### Weak or likely-to-change areas

- `contracts_service.py` and some interface placeholder files look transitional
- `docs/architecture.md` is stale compared with `ARCHITECTURE.md`
- `configs/` is not yet the operational configuration source despite project intent
- API surface is minimal and not yet the orchestration layer for experiments
- persisted `InferenceRun` and `ScoreOutput` models exist but are not central in the active pipeline

### Verification limitation in this review

I attempted to run the existing Python test suite from the current environment, but Python imports beyond trivial execution hung instead of completing. Because of that, I am treating validation status as:

- strong from code trace plus existing tests on disk
- partially confirmed by documented manual validation
- not freshly re-executed successfully in this session

## Part E: New Engineer Briefing

### How EchoMind works today

EchoMind currently runs a deterministic research pipeline over synthetic autobiographical memories. The planner produces six cue families, the renderer writes deterministic text/audio/video placeholder artifacts, the TRIBE layer preprocesses those stimuli into a text-first smoke path, a stub client emits deterministic response scores, the scoring layer combines those scores with explicit modality/personalization heuristics, and the experiment layer ranks and groups results for dashboard and report inspection.

There is also a separate DB/API slice centered on one seeded demo memory. That path is useful for persistence and API shells, but it is not the source of truth for the main experiment workflow.

### What to run first

1. `python -m scripts.seed_demo_data`
2. `python -m scripts.run_demo_comparison`
3. `python -m scripts.run_multi_memory_experiments`
4. `python -m scripts.export_report_artifacts`
5. `streamlit run apps/dashboard/app.py`

### Where to look for the main logic

- planner: `echomind/cues/planner.py`
- renderer: `echomind/media/renderer.py`
- TRIBE boundary: `echomind/tribe/`
- scoring: `echomind/scoring/`
- experiments: `echomind/experiments/reports.py`
- synthetic dataset: `echomind/demo_data/memories.py`

### What not to assume

- Do not assume the DB powers the experiment pipeline today.
- Do not assume TRIBE inference is real model execution.
- Do not assume narration/slideshow are truly multimodal in the current smoke path.
- Do not assume `configs/` is the live config backbone yet.
- Do not assume README/docs are all equally current; `ARCHITECTURE.md` is closer to repo truth than `docs/architecture.md`.

### Top 10 files to read first

1. `ARCHITECTURE.md`
2. `MANUAL_TESTS.md`
3. `echomind/cues/planner.py`
4. `echomind/media/renderer.py`
5. `echomind/tribe/infer.py`
6. `echomind/tribe/preprocess.py`
7. `echomind/scoring/pipeline.py`
8. `echomind/experiments/reports.py`
9. `echomind/demo_data/memories.py`
10. `apps/dashboard/app.py`

## Critical Findings

### Strong architecture choices

- The pipeline is split into clean contract boundaries: planning, rendering, preprocessing/inference, scoring, and experiments.
- Heuristic factors are explicit and separated from response-derived signals.
- Artifact persistence is deterministic and auditable.
- Stub adapters are isolated behind interfaces that can be replaced later.
- The synthetic dataset is well-structured and intentionally varied.

### Current bottlenecks

- The main experiment pipeline does not run through persisted DB entities.
- The TRIBE path only meaningfully supports text-first smoke testing.
- Media “rendering” is structurally useful but content generation is placeholder-based.
- Reported delivery-mode results are constrained by the text-only inference path.

### Hidden assumptions

- Personalized-vs-generic results are materially affected by stub hash behavior, not just cue quality.
- Slideshow support depends on parseable URI-bearing slide prompt strings.
- Dashboard “data loading” is mostly rerunning the pipeline, not browsing a stable experiment store.
- The single DB-seeded memory and the 12-memory synthetic dataset are separate truths.

### Technical debt / likely refactor points

- Unify or clearly separate DB-backed runtime data and synthetic experiment dataset flows.
- Retire or isolate placeholder modules like `contracts_service.py` so extension points are unambiguous.
- Move scoring weights and experiment knobs toward real config files under `configs/`.
- Decide whether experiment orchestration should remain script-first or become a service/API layer.
- Introduce a real TRIBE adapter and expand preprocess support before drawing conclusions from modality comparisons.

