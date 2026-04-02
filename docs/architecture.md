# Architecture (Stub)

## Intent

This document will define the modular architecture for in-silico cue generation, rendering, simulation-based evaluation, and transparent scoring.

## Current Layers

- `apps/api`: HTTP entrypoint and route wiring
- `apps/dashboard`: Streamlit shell for experiment inspection
- `apps/worker`: Celery worker entrypoint
- `echomind/core`: settings, logging, enums, shared utilities
- `echomind/db`: DB base/session and model/schema namespaces
- `echomind/memory`: autobiographical memory domain interfaces
- `echomind/cues`: cue planning/generation interfaces
- `echomind/media`: multimodal rendering interfaces
- `echomind/tribe`: TRIBE integration wrapper interfaces
- `echomind/scoring`: interpretable scoring interfaces
- `echomind/experiments`: experiment orchestration interfaces

## Notes

Implementation remains intentionally minimal in this phase to support clean extension in later tasks.
