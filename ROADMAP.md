# ROADMAP

## Completed Milestones
- M1: Bootstrap scaffold (API/dashboard/worker/tooling/docs stubs)
- M2: Persistence domain models, migrations, seed data, CRUD/services, API readback
- M3: Project-wide rename to EchoMind
- M4: Contract tightening + deterministic cue planner
- M5: Deterministic media rendering layer with swappable stub adapters and tests
- M6: TRIBE integration wrapper and text-first end-to-end smoke inference path

## Current Milestone
- M6 hardening: expand modality coverage beyond text-first preprocess and solidify run artifact schema

## Next 3 Milestones
1. M7: Transparent scoring pipeline
- add decomposable submetrics and composite score wiring
- persist score outputs linked to inference run artifacts

2. M8: Experiment orchestration
- deterministic experiment runs over cue/render/inference/score pipeline
- add config-driven run definitions and basic dashboard result views

3. M9: TRIBE execution backend upgrade
- add environment-backed TRIBE client implementation
- retain stub fallback for deterministic/local test execution

## Stretch Goals
- optional real TTS backend
- optional real ffmpeg slideshow rendering backend
- richer dashboard comparison workflows and run filtering

## Open Technical Risks
- contract drift between renderer outputs and evolving TRIBE input expectations
- artifact-path portability across local/dev/container environments
- balancing deterministic tests with environment-dependent real model execution
- ensuring non-clinical messaging remains explicit as features grow
