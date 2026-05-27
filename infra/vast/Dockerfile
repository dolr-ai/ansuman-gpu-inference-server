FROM vllm/vllm-openai:latest

ENV APP_DIR=/app \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        redis-server \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL \
      https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
      -o /usr/local/bin/cloudflared \
    && chmod +x /usr/local/bin/cloudflared

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY backend ./backend
COPY docs ./docs
COPY infra ./infra

RUN uv sync --frozen --no-dev

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD /bin/bash /app/infra/vast/healthcheck.sh

CMD ["/bin/bash", "/app/infra/vast/startup.sh"]
