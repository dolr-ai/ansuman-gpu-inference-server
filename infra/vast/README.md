# Vast Deployment Files

This directory contains the single-container Vast.ai deployment scaffold.

Process layout:

- FastAPI gateway on `0.0.0.0:8000`.
- vLLM on `127.0.0.1:8001`.
- Cloudflare Tunnel token mode for `model.ansuman.yral.com`.
- Optional local Redis on `127.0.0.1:6379`.

Start command:

```bash
/bin/bash /app/infra/vast/startup.sh
```

Read `docs/vast-deployment.md` before using this for a real instance. The current
backend exposes `/health`, `/v1/models`, and `/v1/chat/completions`; auth,
rate limits, and accounting are still later implementation phases.
