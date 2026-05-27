# GPU Inference Backend

Backend skeleton for a GPU inference gateway. The target deployment is a Vast.ai GPU
container exposed through Cloudflare Tunnel at `https://model.ansuman.yral.com`.

Current implemented API: `/health`, `/v1/models`, and OpenAI-compatible
`/v1/chat/completions` through a FastAPI gateway on port `8000`, forwarding to
private local vLLM on port `8001`.

## Development

```bash
uv sync
uv run uvicorn backend.main:app --reload
```

Deployment planning:

- `docs/plan.md`
- `docs/todo.md`
- `docs/vast-deployment.md`
- `infra/vast/`
