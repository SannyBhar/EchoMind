# EchoMind / Remembra MVP Scaffold

Remembra is a **non-clinical, research-only** platform for generating and comparing personalized multimodal memory cues using TRIBE v2 as a simulation and evaluation layer.

## Non-Clinical Scope

This codebase is for in-silico experimentation and cue ranking only.
It does **not** provide diagnosis, treatment, or clinical assessment.

## MVP Scaffold Contents

- FastAPI backend shell with health endpoints
- Streamlit dashboard shell
- Celery worker scaffold with Redis broker
- SQLAlchemy-ready database session scaffold
- Modular package layout for memory, cues, media, TRIBE wrapper, scoring, and experiments
- Developer tooling for linting, formatting, testing, and pre-commit

## Quickstart (Local)

1. Create and activate a Python 3.11+ environment.
2. Install dependencies:
   ```bash
   make install
   ```
3. Run API:
   ```bash
   make dev-api
   ```
4. Run dashboard:
   ```bash
   make dev-dashboard
   ```
5. Run worker:
   ```bash
   make dev-worker
   ```
6. Run tests:
   ```bash
   make test
   ```

## Quickstart (Docker Compose)

```bash
docker compose up --build
```

- API: http://localhost:8000/health
- Dashboard: http://localhost:8501

## Documentation Stubs

- [Architecture](docs/architecture.md)
- [Ethics and Non-Clinical Limitations](docs/ethics.md)
- [Roadmap](docs/roadmap.md)
