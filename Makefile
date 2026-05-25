VENV := .venv
ENV_FILE := .env
UV := uv
UV_RUN := $(UV) run --env-file $(ENV_FILE)

.PHONY: install venv env dev lint format test-unit test-integration test migrate run-api run-worker run-flusher smoke bench

env: $(ENV_FILE)

$(ENV_FILE):
	cp .env.example $(ENV_FILE)

venv: $(VENV)/bin/python

$(VENV)/bin/python:
	$(UV) venv $(VENV)

install: env venv
	$(UV) sync

dev: env venv
	$(UV_RUN) uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

lint: env venv
	$(UV_RUN) ruff check backend tests
	$(UV_RUN) mypy backend

format: env venv
	$(UV_RUN) ruff format backend tests
	$(UV_RUN) ruff check backend tests --fix

test-unit: env venv
	$(UV_RUN) pytest tests/unit -q

test-integration: env venv
	$(UV_RUN) pytest tests/integration -q

test: env venv
	$(UV_RUN) pytest tests -q

migrate: env venv
	$(UV_RUN) alembic upgrade head

run-api: env venv
	$(UV_RUN) uvicorn backend.main:app --host 127.0.0.1 --port 8000

run-worker: env venv
	$(UV_RUN) python -m backend.workers.batch_worker

run-flusher: env venv
	$(UV_RUN) python -m backend.workers.analytics_flusher

smoke: env venv
	$(UV_RUN) python -m backend.scripts.smoke_test

bench: env venv
	$(UV_RUN) python -m backend.scripts.benchmark
