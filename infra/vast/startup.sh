#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
SUPERVISOR_CONFIG="${SUPERVISOR_CONFIG:-${APP_DIR}/infra/vast/supervisord.conf}"

cd "${APP_DIR}"

if [[ ! -f "${SUPERVISOR_CONFIG}" ]]; then
  echo "Supervisor config not found: ${SUPERVISOR_CONFIG}" >&2
  exit 1
fi

exec supervisord -c "${SUPERVISOR_CONFIG}"
