# Vast Deployment Runbook

This runbook deploys the current backend skeleton and the planned vLLM sidecar layout
on a single Vast.ai GPU instance.

Current limitation: the app only implements `/health`. The deployment can prove the
Vast and Cloudflare path now, but `/v1/models` and `/v1/chat/completions` still need
backend implementation before the endpoint is a real inference API.

## Required Inputs

- Vast.ai GPU instance with enough VRAM for `VLLM_MODEL`.
- Cloudflare Tunnel token for `model.ansuman.yral.com`.
- Model id for vLLM, for example a Hugging Face model id.
- Optional external `DATABASE_URL`, `CLICKHOUSE_URL`, and `SENTRY_DSN` for later phases.

## Runtime Layout

```text
cloudflared -> http://127.0.0.1:8000 -> FastAPI gateway
FastAPI gateway -> http://127.0.0.1:8001 -> vLLM
FastAPI gateway -> Postgres, Redis, ClickHouse as features are implemented
```

Do not point Cloudflare directly to vLLM. The gateway must remain the public contract.

## Environment

Create a `.env` on the instance using `infra/vast/env.production.example` as the
template. The minimum useful values are:

```bash
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
PUBLIC_BASE_URL=https://model.ansuman.yral.com
VLLM_HOST=127.0.0.1
VLLM_PORT=8001
VLLM_BASE_URL=http://127.0.0.1:8001
VLLM_MODEL=<model-id>
RUN_VLLM=1
RUN_CLOUDFLARED=1
CLOUDFLARE_TUNNEL_TOKEN=<token>
```

Keep the real token out of git.

## Build Image

From the `gpu-inference-backend` directory:

```bash
docker build -f infra/vast/Dockerfile -t gpu-inference-backend:vast .
```

For Vast, either push that image to a registry and use it as the instance image, or
build it on the instance after cloning the repo.

## Start Command

Use this container command:

```bash
/bin/bash /app/infra/vast/startup.sh
```

The startup script runs supervisor, which manages:

- `api`: FastAPI on port `8000`.
- `vllm`: local OpenAI-compatible vLLM server on port `8001`.
- `cloudflared`: Cloudflare Tunnel token mode.
- `redis`: optional local Redis, disabled unless `RUN_REDIS=1`.

## Validation

On the Vast instance:

```bash
supervisorctl -c /app/infra/vast/supervisord.conf status
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8001/v1/models
```

From outside the instance:

```bash
curl -fsS https://model.ansuman.yral.com/health
```

Expected current public health response:

```json
{"status":"ok"}
```

## Operational Notes

- If `cloudflared` fails, check `CLOUDFLARE_TUNNEL_TOKEN` and the tunnel route in the
  Cloudflare dashboard.
- If `vllm` fails, check GPU memory, `VLLM_MODEL`, and `VLLM_ARGS`.
- If the API fails, check the supervisor log for the `api` program.
- Keep vLLM on `127.0.0.1:8001`; changing it to `8000` conflicts with the gateway.
- Do not expose Redis, vLLM, Postgres, or ClickHouse directly to the public internet.

## Cutover Gate

Only `/health` should be considered production-ready today. Do not cut production
clients over to `/v1/chat/completions` until the gateway route, auth, rate limits, and
vLLM proxy tests are implemented.
