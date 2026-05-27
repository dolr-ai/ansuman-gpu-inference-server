#!/usr/bin/env bash
set -euo pipefail

if [[ "${RUN_REDIS:-0}" != "1" ]]; then
  echo "redis disabled because RUN_REDIS=${RUN_REDIS:-unset}"
  exec tail -f /dev/null
fi

REDIS_PORT="${REDIS_PORT:-6379}"

exec redis-server \
  --bind 127.0.0.1 \
  --port "${REDIS_PORT}" \
  --save "" \
  --appendonly no
