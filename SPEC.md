# SPEC

## Project Mission
EchoMind is a non-clinical research platform for generating and comparing personalized multimodal memory cues using TRIBE v2 as a simulation/evaluation layer.

## Non-Clinical Framing
- EchoMind is research software, not a medical product.
- It does not diagnose, treat, prevent, or assess disease.
- It does not claim memory improvement efficacy.
- Outputs are simulation-oriented artifacts for in-silico comparison only.

## Project Overview
EchoMind currently supports:
- autobiographical memory records and related entities (people/place/assets)
- deterministic cue planning contracts and planner logic
- deterministic media rendering contracts and rendering stubs
- TRIBE integration wrapper boundary with deterministic smoke-test execution path
- transparent scoring submetrics and weighted composite ranking outputs
- grouped experiment comparisons (personalization, tone, delivery mode)
- simulation request/result summary contracts with persisted inference artifacts
- persistence scaffolding, migrations, seed data, API read endpoints, and dashboard shell

## Research Objective
Produce reproducible candidate cue sets and rendered stimuli that can be evaluated via TRIBE wrappers and later transparent scoring.

## Working Hypotheses
1. deterministic cue families provide stable baselines for simulation comparison
2. multimodal cue delivery (text, narration, slideshow+narration) may yield distinct simulated response profiles
3. explicit traceability metadata improves reproducibility and analysis quality

## Non-Goals
- clinical decision support
- therapeutic intervention claims
- production media generation quality optimization
- autonomous LLM-based cue generation in MVP

## Scientific Limitations
- current TRIBE execution uses a deterministic stub client by default
- first smoke path supports text-first preprocessing for reliability
- current scoring includes explicit heuristic factors for modality and personalization
- no human outcome validation loop in current MVP

## Ethical Framing
The system must remain explicit about non-clinical use and avoid overclaiming scientific capability beyond implemented behavior.

## Current MVP Definition
MVP includes deterministic end-to-end preparation from memory context to planned cues, rendered stimuli, and simulation wrapper outputs:
- memory + assets persisted and retrievable
- deterministic cue planner emits validated cue variants
- deterministic media renderer emits validated rendered stimuli and local artifacts
- TRIBE integration path preprocesses stimuli, runs wrapper inference, persists raw outputs and summaries
- scoring layer emits decomposable metrics and weighted composite scores
- experiment layer summarizes ranked outputs across personalization/tone/modality slices
- contracts enforce mode/state invariants across pipeline boundaries

## Completed Milestones
- M1: repository scaffold and service shells
- M2: persistence layer, SQLAlchemy models, migrations, seed script, CRUD tests
- M3: package rename to EchoMind and contract baseline
- M4: deterministic cue planner with traceability metadata
- M5: deterministic media rendering layer (text, narration, slideshow+narration) with tests
- M6: TRIBE integration wrapper + first end-to-end text smoke inference path with saved artifacts
- M7: scoring + experiment comparison layer with deterministic demo report outputs
- M7.1: manual validation checklist captured in `MANUAL_TESTS.md`

## Immediate Next Milestone
M8: dashboard enrichment and product-facing experience APIs for viewing cue rankings and experiment slices.
