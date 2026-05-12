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
- M8: Minimal Streamlit experiment inspection dashboard over validated deterministic pipeline
- M9: Reproducible 12-memory synthetic demo dataset + multi-memory experiment runner with per-memory and aggregated outputs (JSON + CSV)
- M9.1: Stronger cue semantic separation (generic vs autobiographical, warm vs neutral, slideshow scene references); dataset quality improvements; semantic regression tests
- M9.2: Frozen `paper.v1.0` experiment configuration, report-export script (CSVs + simple plots), and CS439 paper outline / report-artifact docs

## Current Milestone
- M10: product-facing experience APIs and richer dashboard filtering/report navigation over existing pipeline artifacts

## Next 3 Milestones
1. M10.1: dashboard filtering + report navigation
- add run-history inspection and comparison report selection
- add lightweight filters for modality/tone/personalization slices
- optionally surface multi-memory aggregated dimension charts

2. M11: TRIBE execution backend upgrade
- add environment-backed TRIBE client implementation
- retain stub fallback for deterministic/local test execution

3. M12: persistence hardening for scoring + experiment outputs
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
