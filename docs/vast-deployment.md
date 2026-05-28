# Vast Deployment

## Current Bootstrap State

Status as of 2026-05-28:

```text
Vast SSH: ssh -i /home/ansuman/.ssh/id_ed25519_vast -p 21591 root@136.38.182.51
Vast device name: vast-gpu-inference-38274334
Tailscale IP: 100.120.175.118
Tailnet: ansuman00edu@gmail.com
GPU: NVIDIA RTX PRO 4000 Blackwell, 24 GiB
Existing vLLM: Qwen/Qwen3-8B-FP8 on 127.0.0.1:18000
```

Tailscale is installed and logged in on the Vast container. Because this
container does not expose `/dev/net/tun`, `tailscaled` is running in userspace
networking mode:

```text
tailscaled --tun=userspace-networking --state=/var/lib/tailscale/tailscaled.state --socket=/run/tailscale/tailscaled.sock --socks5-server=127.0.0.1:1055
```

Tailscale peer checks from Vast passed for:

```text
ansuman-1: 100.78.17.101
ansuman-2: 100.79.99.107
```

Important: this is not a production app deployment yet. The backend code is not
complete, so the Vast instance should only be treated as a network/bootstrap
target for now. A copy may exist at `/workspace/gpu-inference-backend` from the
initial bootstrap pass, but it is not the source of truth and should be re-synced
after the backend implementation is ready.

Normal Postgres/ClickHouse client connections may need either a Vast container
with `/dev/net/tun`/network admin support or explicit local proxying through the
userspace Tailscale SOCKS listener on `127.0.0.1:1055`.

## Private Service Routes

For the Postgres private network path from Vast, use
`docs/postgres-connectivity.md`.

For the ClickHouse private network path from Vast, use
`docs/clickhouse-connectivity.md`.

Cloudflare tunnel remains for public FastAPI HTTP traffic:

```text
model.ansuman.yral.com -> http://127.0.0.1:8000
```

Postgres must use Tailscale TCP, not Cloudflare HTTP proxying.
