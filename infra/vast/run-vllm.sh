#!/usr/bin/env bash
set -euo pipefail

if [[ "${RUN_VLLM:-1}" != "1" ]]; then
  echo "vLLM disabled because RUN_VLLM=${RUN_VLLM:-unset}"
  exec tail -f /dev/null
fi

if [[ -z "${VLLM_MODEL:-}" ]]; then
  echo "VLLM_MODEL is required when RUN_VLLM=1" >&2
  exit 1
fi

VLLM_HOST="${VLLM_HOST:-127.0.0.1}"
VLLM_PORT="${VLLM_PORT:-8001}"

exec python -m vllm.entrypoints.openai.api_server \
  --host "${VLLM_HOST}" \
  --port "${VLLM_PORT}" \
  --model "${VLLM_MODEL}" \
  ${VLLM_ARGS:-}
