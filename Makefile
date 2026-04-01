.PHONY: install dev-api dev-dashboard dev-worker lint format test migrate seed up down

install:
	pip install -e .[dev]

dev-api:
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

dev-dashboard:
	streamlit run apps/dashboard/app.py --server.port 8501

dev-worker:
	celery -A apps.worker.main.celery_app worker --loglevel=INFO

lint:
	ruff check .

format:
	ruff format .

test:
	pytest

migrate:
	alembic upgrade head

seed:
	python -m scripts.seed_demo_data

up:
	docker compose up --build

down:
	docker compose down
