# ROADMAP

## Completed Milestones
- M1: Bootstrap scaffold (API/dashboard/worker/tooling/docs stubs)
- M2: Persistence domain models, migrations, seed data, CRUD/services, API readback
- M3: Project-wide rename to EchoMind
- M4: Contract tightening + deterministic cue planner
- M5: Deterministic media rendering layer with swappable stub adapters and tests
- M6: TRIBE integration wrapper and text-first end-to-end smoke inference path
- M7: Transparent scoring + experiment comparison layer with deterministic report output
- M7.1: Manual validation checklist codified in `MANUAL_TESTS.md`

## Current Milestone
- M8: dashboard enrichment and product-facing experience APIs over existing pipeline artifacts

## Next 3 Milestones
1. M8.1: dashboard comparison views and API read models
- expose ranked cues and grouped experiment summaries via stable API contracts
- add dashboard sections for run artifacts and score breakdowns

2. M9: TRIBE execution backend upgrade
- add environment-backed TRIBE client implementation
- retain stub fallback for deterministic/local test execution

3. M10: persistence hardening for scoring + experiment outputs
- store score breakdowns and experiment summaries as first-class persisted records
- link DB records to deterministic artifact manifests for auditability

## Stretch Goals
- optional real TTS backend
- optional real ffmpeg slideshow rendering backend
- batch experiment orchestration and run-level config registry

## Open Technical Risks
- contract drift between renderer outputs and evolving TRIBE input expectations
- artifact-path portability across local/dev/container environments
- balancing deterministic tests with environment-dependent TRIBE backends
- ensuring non-clinical messaging remains explicit as features grow
