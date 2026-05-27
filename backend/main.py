"""Application entrypoint."""

from fastapi import FastAPI

from backend.api.routes.chat_completions import router as chat_completions_router
from backend.api.routes.health import router as health_router
from backend.api.routes.models import router as models_router
from backend.middlewares.request_id import request_id_middleware


def create_app() -> FastAPI:
    """Build the FastAPI application."""
    app = FastAPI(title="GPU Inference Backend")
    app.middleware("http")(request_id_middleware)
    app.include_router(health_router)
    app.include_router(models_router)
    app.include_router(chat_completions_router)
    return app


app = create_app()
