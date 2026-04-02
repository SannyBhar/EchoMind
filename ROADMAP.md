# ROADMAP

## Completed Milestones
- M1: Bootstrap scaffold (API/dashboard/worker/tooling/docs stubs)
- M2: Persistence domain models, migrations, seed data, CRUD/services, API readback
- M3: Project-wide rename to EchoMind
- M4: Contract tightening + deterministic cue planner
- M5: Deterministic media rendering layer with swappable stub adapters and tests

## Current Milestone
- M5 hardening: media artifact conventions and contract stability for inference handoff

## Next 3 Milestones
1. M6: TRIBE wrapper integration
- implement inference adapter boundary using `InferenceRequest`
- persist `InferenceRun` lifecycle and raw artifact metadata

2. M7: Transparent scoring pipeline
- add decomposable submetrics and composite score wiring
- persist `ScoreOutput` components and expose read APIs

3. M8: Experiment orchestration
- deterministic experiment runs over cue/render/inference/score pipeline
- add config-driven run definitions and basic dashboard result views

## Stretch Goals
- optional real TTS backend
- optional real ffmpeg slideshow rendering backend
- richer dashboard comparison workflows and run filtering

## Open Technical Risks
- contract drift between planner/renderer and future TRIBE adapter expectations
- artifact-path portability across local/dev/container environments
- maintaining deterministic behavior as adapters become more capable
- ensuring non-clinical messaging remains explicit as features grow
