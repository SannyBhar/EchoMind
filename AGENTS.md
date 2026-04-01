# AGENTS.md

## Project: EchoMind

Remembra is a research-grade, non-clinical platform for generating and comparing personalized multimodal memory cues using TRIBE v2 as a brain-response simulation and evaluation layer.

This repository must remain rigorously scoped:
- It is NOT a diagnostic tool.
- It is NOT a treatment tool.
- It is NOT a medical device.
- It must NOT claim memory improvement, therapeutic efficacy, disease prediction, or clinical validity.
- It is an in-silico experimentation and ranking platform.

## Product intent

The system should eventually support:
1. structured autobiographical memory records
2. systematic cue generation
3. media rendering into text/audio/video stimuli
4. TRIBE-based inference wrappers
5. transparent scoring and ranking
6. experiment orchestration
7. dashboard-based result inspection
8. optional later human-feedback comparison

## Engineering priorities

Optimize for:
- clean architecture
- reproducibility
- auditability
- explicit limitations
- strong typing
- testability
- config-driven experiments
- modular services

Do not optimize for:
- flashy UI
- premature scale
- vague “AI magic”
- clinical framing
- hidden heuristics

## Build philosophy

Prefer:
- small, reviewable changes
- explicit interfaces
- code that is easy to extend in later tasks
- configuration over hard-coded behavior
- stubs/placeholders when a subsystem is not yet implemented

Avoid:
- giant rewrites
- introducing unrelated dependencies
- implementing future phases unless explicitly asked
- inventing scientific claims beyond what the code actually does

## Current recommended stack

- Python 3.11+
- FastAPI
- Streamlit
- SQLAlchemy
- Pydantic
- Postgres
- Redis
- Celery
- Pytest
- Ruff
- Docker Compose

## Expected repository shape

- `apps/api/` for FastAPI app entrypoint
- `apps/dashboard/` for Streamlit app
- `apps/worker/` for background worker entrypoint
- `remembra/core/` for settings, logging, enums, utilities
- `remembra/db/` for database base/session/models/schemas
- `remembra/memory/` for autobiographical entities and services
- `remembra/cues/` for cue planning and generation
- `remembra/media/` for rendering helpers
- `remembra/tribe/` for TRIBE integration wrapper
- `remembra/scoring/` for metrics and composite scoring
- `remembra/experiments/` for experiment definitions and runners
- `remembra/api/` for API routes and dependencies
- `configs/` for app, scoring, and experiment configs
- `tests/` for unit/integration/e2e tests
- `docs/` for architecture, ethics, roadmap, and experiment specs

## Domain framing rules

Always preserve these distinctions in docs, comments, and UI copy:

Say:
- “predicted cortical response”
- “in-silico evaluation”
- “cue ranking”
- “simulation-based comparison”
- “candidate cue for later validation”

Do not say:
- “best therapy”
- “improves memory”
- “detects dementia”
- “restores recall”
- “clinically validated”
- “brain-proven”

## Coding rules

- Use type hints throughout.
- Prefer Pydantic schemas for external contracts.
- Prefer SQLAlchemy 2.0 style.
- Keep functions small and composable.
- Keep side effects at boundaries.
- Use clear names over clever names.
- Add docstrings for public modules and important classes.
- Keep comments useful and sparse.
- Avoid dead code and placeholder complexity.
- Put constants and config in the proper config/settings layer.

## Testing rules

When you implement meaningful code:
- add or update tests
- prefer unit tests first
- add integration tests for API, DB, worker, or pipeline boundaries
- do not mark work complete if it is untested unless the task explicitly says scaffolding only

## Task execution rules

For complex tasks:
1. inspect the repo first
2. summarize the plan briefly
3. implement only the requested scope
4. run relevant tests/lint if available
5. summarize changes and any follow-up work

Do not:
- silently broaden scope
- refactor unrelated modules without a strong reason
- remove existing docs or constraints
- change architecture direction without explaining why

## TRIBE-specific rules

TRIBE integration must be isolated behind a wrapper/client layer.
Do not spread model-specific logic across the codebase.
Assume TRIBE outputs are simulation artifacts for research use, not ground truth of recall.
Any scoring built on TRIBE outputs must remain interpretable and configurable.

## Cue generation rules

Cue generation should be systematic, not ad hoc.
Prefer:
- factorized cue families
- templates
- schema-validated outputs
- reproducible config-driven generation

Avoid:
- one-off prompt spaghetti
- hidden prompt assumptions
- mixing generation logic with UI logic

## Scoring rules

Scoring must be transparent.
Every composite score should be decomposable into named submetrics.
Weights should live in config where practical.
Metadata-based bonuses must be clearly separated from model-derived metrics.

## UI and docs rules

The dashboard and docs should visibly state:
- non-clinical use
- simulation-only framing
- research limitations
- no efficacy claims

## Definition of done

A task is done only when:
- requested scope is completed
- files remain organized and readable
- tests relevant to the task pass, if tests exist
- new behavior is documented where needed
- the result supports later phases cleanly

## Preferred response format from Codex

When finishing a task, provide:
1. what changed
2. files added/edited
3. how to verify
4. risks or follow-ups
