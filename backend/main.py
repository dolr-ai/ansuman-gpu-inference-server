"""Application entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from backend.api.routes.batch_jobs import router as batch_jobs_router
from backend.api.routes.chat_completions import router as chat_completions_router
from backend.api.routes.health import router as health_router
from backend.api.routes.metrics import router as metrics_router
from backend.api.routes.models import router as models_router
from backend.core.config import Settings, get_settings
from backend.core.lifecycle import shutdown, startup
from backend.middlewares.auth import ApiKeyAuthMiddleware
from backend.middlewares.error_handler import install_error_handlers
from backend.middlewares.request_id import RequestIdMiddleware
from backend.services.observability.metrics import MetricsMiddleware
from backend.services.vllm.client import VLLMClient


def create_app(
    settings: Settings | None = None,
    vllm_client: Any | None = None,
    auth_service: Any | None = None,
    admission_service: Any | None = None,
    token_estimator: Any | None = None,
    audit_service: Any | None = None,
    analytics_collector: Any | None = None,
    batch_service: Any | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""
    resolved_settings = settings or get_settings()
    owns_vllm_client = vllm_client is None

    @asynccontextmanager
    async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
        app_instance.state.vllm_client = vllm_client or VLLMClient(resolved_settings.vllm_base_url)
        await startup(app_instance, resolved_settings)
        try:
            yield
        finally:
            if owns_vllm_client:
                await app_instance.state.vllm_client.close()
            await shutdown(app_instance)

    app_instance = FastAPI(title="GPU Inference Backend", lifespan=lifespan)
    if auth_service is not None:
        app_instance.state.auth_service = auth_service
    if admission_service is not None:
        app_instance.state.admission_service = admission_service
    if token_estimator is not None:
        app_instance.state.token_estimator = token_estimator
    if audit_service is not None:
        app_instance.state.audit_service = audit_service
    if analytics_collector is not None:
        app_instance.state.analytics_collector = analytics_collector
    if batch_service is not None:
        app_instance.state.batch_service = batch_service
    app_instance.add_middleware(ApiKeyAuthMiddleware)
    app_instance.add_middleware(RequestIdMiddleware)
    app_instance.add_middleware(MetricsMiddleware)
    install_error_handlers(app_instance)
    app_instance.include_router(health_router)
    app_instance.include_router(models_router)
    app_instance.include_router(metrics_router)
    app_instance.include_router(chat_completions_router)
    app_instance.include_router(batch_jobs_router)
    return app_instance


app = create_app()
