# Architecture (Stub)

## Intent

This document will define the modular architecture for in-silico cue generation, rendering, simulation-based evaluation, and transparent scoring.

## Current Layers

- `apps/api`: HTTP entrypoint and route wiring
- `apps/dashboard`: Streamlit shell for experiment inspection
- `apps/worker`: Celery worker entrypoint
- `remembra/core`: settings, logging, enums, shared utilities
- `remembra/db`: DB base/session and model/schema namespaces
- `remembra/memory`: autobiographical memory domain interfaces
- `remembra/cues`: cue planning/generation interfaces
- `remembra/media`: multimodal rendering interfaces
- `remembra/tribe`: TRIBE integration wrapper interfaces
- `remembra/scoring`: interpretable scoring interfaces
- `remembra/experiments`: experiment orchestration interfaces

## Notes

Implementation remains intentionally minimal in this phase to support clean extension in later tasks.
