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
- simulation request/result summary contracts
- persistence scaffolding, migrations, seed data, API read endpoints, and dashboard shell

## Research Objective
Produce reproducible candidate cue sets and rendered stimuli that can later be evaluated via TRIBE wrappers and transparent scoring.

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
- current rendering layer uses deterministic stubs for audio/video artifacts
- no TRIBE simulation execution yet in the media layer
- no scoring formulas applied to rendered stimuli yet
- no human outcome validation loop in current MVP

## Ethical Framing
The system must remain explicit about non-clinical use and avoid overclaiming scientific capability beyond implemented behavior.

## Current MVP Definition
MVP includes deterministic end-to-end preparation from memory context to planned cues and rendered-stimulus manifests:
- memory + assets persisted and retrievable
- deterministic cue planner emits validated cue variants
- deterministic media renderer emits validated rendered stimuli and local artifacts
- contracts enforce mode/state invariants for downstream inference integration

## Completed Milestones
- M1: repository scaffold and service shells
- M2: persistence layer, SQLAlchemy models, migrations, seed script, CRUD tests
- M3: package rename to EchoMind and contract baseline
- M4: deterministic cue planner with traceability metadata
- M5: deterministic media rendering layer (text, narration, slideshow+narration) with tests

## Immediate Next Milestone
M6: TRIBE wrapper integration using `InferenceRequest` + `StimulusManifest` contracts and persisted `InferenceRun`/`ScoreOutput` wiring.
