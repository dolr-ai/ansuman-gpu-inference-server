"""Chat completion routes."""

from collections.abc import AsyncIterator
from time import perf_counter
from typing import Any, Protocol

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from backend.core.config import Settings
from backend.core.constants import REQUEST_ID_HEADER
from backend.core.errors import AppError
from backend.db.redis import RedisClient
from backend.schemas.chat_completion import ChatCompletionRequest
from backend.services.auth.api_key_service import AuthContext, ensure_model_allowed
from backend.services.rate_limit.admission import AdmissionLease, AdmissionService
from backend.services.rate_limit.concurrency_limiter import ConcurrencyLimiter
from backend.services.rate_limit.quota_reserver import QuotaReserver
from backend.services.rate_limit.rate_limiter import RateLimiter
from backend.services.vllm.payload_mapper import normalize_chat_completion_payload
from backend.services.vllm.stream import (
    DONE_LINE,
    SSE_HEADERS,
    SSE_MEDIA_TYPE,
    ensure_done_event,
    stream_with_heartbeats,
)

router = APIRouter(prefix="/v1", tags=["chat"])


class AdmissionController(Protocol):
    async def admit(
        self, auth_context: AuthContext, *, estimated_tokens: int = 0
    ) -> AdmissionLease: ...


class ChatCompletionClient(Protocol):
    async def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    def stream_chat_completion(self, payload: dict[str, Any]) -> AsyncIterator[str]: ...


@router.post("/chat/completions", response_model=None)
async def create_chat_completion(
    request_body: ChatCompletionRequest,
    request: Request,
) -> JSONResponse | StreamingResponse:
    """Proxy OpenAI-compatible chat completions to vLLM."""
    auth_context = getattr(request.state, "auth_context", None)
    if not isinstance(auth_context, AuthContext):
        raise AppError(
            message="Missing API key",
            code="missing_api_key",
            status_code=401,
            type="invalid_request_error",
        )
    ensure_model_allowed(auth_context, request_body.model)

    admission_service = _get_or_create_admission_service(request)
    admission_lease = await admission_service.admit(auth_context)
    payload = normalize_chat_completion_payload(request_body)
    request_id = getattr(request.state, "request_id", None)
    headers = {REQUEST_ID_HEADER: request_id} if request_id is not None else None
    client: ChatCompletionClient = request.app.state.vllm_client

    if request_body.stream:
        return StreamingResponse(
            _stream_response(client, payload, request, admission_lease),
            media_type=SSE_MEDIA_TYPE,
            headers={**SSE_HEADERS, **(headers or {})},
        )

    try:
        response = await client.create_chat_completion(payload)
        return JSONResponse(content=response, headers=headers)
    finally:
        await admission_lease.release()


async def _stream_response(
    client: ChatCompletionClient,
    payload: dict[str, Any],
    request: Request,
    admission_lease: AdmissionLease | None = None,
) -> AsyncIterator[str]:
    started_at = perf_counter()
    first_token_seen = False
    upstream_stream = client.stream_chat_completion(payload)
    heartbeat_stream = stream_with_heartbeats(upstream_stream)
    event_stream = ensure_done_event(heartbeat_stream)
    try:
        async for event in event_stream:
            if await request.is_disconnected():
                break
            if not first_token_seen and event.startswith("data: ") and event.strip() != DONE_LINE:
                ttft_ms = int((perf_counter() - started_at) * 1000)
                request.state.ttft_ms = ttft_ms
                request.app.state.last_stream_ttft_ms = ttft_ms
                first_token_seen = True
            yield event
    finally:
        await _close_async_iterator(event_stream)
        await _close_async_iterator(heartbeat_stream)
        await _close_async_iterator(upstream_stream)
        if admission_lease is not None:
            await admission_lease.release()


async def _close_async_iterator(iterator: AsyncIterator[str]) -> None:
    aclose = getattr(iterator, "aclose", None)
    if aclose is not None:
        await aclose()


def _get_or_create_admission_service(request: Request) -> AdmissionController:
    admission_service = getattr(request.app.state, "admission_service", None)
    if admission_service is not None:
        return admission_service

    settings: Settings = request.app.state.settings
    redis_client = RedisClient.from_url(settings.redis_url)
    request.app.state.redis_client = redis_client
    admission_service = AdmissionService(
        rate_limiter=RateLimiter(redis_client),
        concurrency_limiter=ConcurrencyLimiter(redis_client),
        quota_reserver=QuotaReserver(),
        rpm_limit=settings.rate_limit_rpm,
        concurrent_request_limit=settings.concurrent_request_limit,
    )
    request.app.state.admission_service = admission_service
    return admission_service
