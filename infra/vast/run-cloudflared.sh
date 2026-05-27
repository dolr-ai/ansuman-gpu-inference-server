#!/usr/bin/env bash
set -euo pipefail

if [[ "${RUN_CLOUDFLARED:-1}" != "1" ]]; then
  echo "cloudflared disabled because RUN_CLOUDFLARED=${RUN_CLOUDFLARED:-unset}"
  exec tail -f /dev/null
fi

if [[ -z "${CLOUDFLARE_TUNNEL_TOKEN:-}" ]]; then
  echo "CLOUDFLARE_TUNNEL_TOKEN is required when RUN_CLOUDFLARED=1" >&2
  exit 1
fi

exec cloudflared tunnel --no-autoupdate run --token "${CLOUDFLARE_TUNNEL_TOKEN}"
