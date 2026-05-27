#!/usr/bin/env bash
set -euo pipefail

APP_PORT="${APP_PORT:-8000}"

exec curl -fsS "http://127.0.0.1:${APP_PORT}/health"
