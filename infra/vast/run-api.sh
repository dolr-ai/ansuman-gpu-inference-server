#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
ENV_FILE="${ENV_FILE:-${APP_DIR}/.env}"
APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8000}"

cd "${APP_DIR}"

if [[ -f "${ENV_FILE}" ]]; then
  exec uv run --env-file "${ENV_FILE}" uvicorn backend.main:app --host "${APP_HOST}" --port "${APP_PORT}"
fi

exec uv run uvicorn backend.main:app --host "${APP_HOST}" --port "${APP_PORT}"
