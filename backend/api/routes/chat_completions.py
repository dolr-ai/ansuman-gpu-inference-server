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
from backend.services.inference.token_accounting import (
    HeuristicTokenEstimator,
    TokenEstimator,
    TokenPlan,
    UsageRecord,
    build_token_plan,
    stream_delta_text,
    usage_from_response,
    usage_from_stream_text,
)
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

    token_estimator = _get_or_create_token_estimator(request)
    settings: Settings = request.app.state.settings
    token_plan = build_token_plan(
        request_body,
        token_estimator,
        max_input_tokens=settings.max_input_tokens,
        max_output_tokens=settings.max_output_tokens,
        max_total_tokens=settings.max_total_tokens,
    )
    admission_service = _get_or_create_admission_service(request)
    admission_lease = await admission_service.admit(
        auth_context, estimated_tokens=token_plan.estimated_total_tokens
    )
    payload = normalize_chat_completion_payload(request_body)
    request_id = getattr(request.state, "request_id", None)
    headers = {REQUEST_ID_HEADER: request_id} if request_id is not None else None
    client: ChatCompletionClient = request.app.state.vllm_client

    if request_body.stream:
        return StreamingResponse(
            _stream_response(
                client, payload, request, admission_lease, token_plan, token_estimator
            ),
            media_type=SSE_MEDIA_TYPE,
            headers={**SSE_HEADERS, **(headers or {})},
        )

    try:
        response = await client.create_chat_completion(payload)
        usage = usage_from_response(response, token_plan, token_estimator)
        await admission_lease.finalize_tokens(actual_tokens=usage.total_tokens)
        _record_usage(request, usage)
        return JSONResponse(content=response, headers=headers)
    except Exception:
        await admission_lease.finalize_tokens(actual_tokens=0, release_all=True)
        _record_usage(
            request,
            UsageRecord(
                prompt_tokens=token_plan.prompt_tokens,
                completion_tokens=0,
                total_tokens=0,
                status="failed",
            ),
        )
        raise
    finally:
        await admission_lease.release()


async def _stream_response(
    client: ChatCompletionClient,
    payload: dict[str, Any],
    request: Request,
    admission_lease: AdmissionLease | None = None,
    token_plan: TokenPlan | None = None,
    token_estimator: TokenEstimator | None = None,
) -> AsyncIterator[str]:
    started_at = perf_counter()
    first_token_seen = False
    upstream_stream = client.stream_chat_completion(payload)
    heartbeat_stream = stream_with_heartbeats(upstream_stream)
    event_stream = ensure_done_event(heartbeat_stream)
    completion_text = ""
    status = "completed"
    try:
        async for event in event_stream:
            if await request.is_disconnected():
                status = "client_disconnected"
                break
            completion_text += stream_delta_text(event)
            if not first_token_seen and event.startswith("data: ") and event.strip() != DONE_LINE:
                ttft_ms = int((perf_counter() - started_at) * 1000)
                request.state.ttft_ms = ttft_ms
                request.app.state.last_stream_ttft_ms = ttft_ms
                first_token_seen = True
            yield event
    except Exception:
        status = "failed"
        raise
    finally:
        await _close_async_iterator(event_stream)
        await _close_async_iterator(heartbeat_stream)
        await _close_async_iterator(upstream_stream)
        if admission_lease is not None and token_plan is not None and token_estimator is not None:
            usage = usage_from_stream_text(
                completion_text,
                token_plan,
                token_estimator,
                status=status,
            )
            await admission_lease.finalize_tokens(
                actual_tokens=usage.total_tokens,
                release_all=status == "failed",
            )
            _record_usage(request, usage)
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
        quota_reserver=QuotaReserver(redis_client, tpm_limit=settings.token_limit_tpm),
        rpm_limit=settings.rate_limit_rpm,
        concurrent_request_limit=settings.concurrent_request_limit,
    )
    request.app.state.admission_service = admission_service
    return admission_service


def _get_or_create_token_estimator(request: Request) -> TokenEstimator:
    token_estimator = getattr(request.app.state, "token_estimator", None)
    if token_estimator is not None:
        return token_estimator
    token_estimator = HeuristicTokenEstimator()
    request.app.state.token_estimator = token_estimator
    return token_estimator


def _record_usage(request: Request, usage: UsageRecord) -> None:
    request.state.usage = usage
    request.app.state.last_usage = usage
    usage_records = getattr(request.app.state, "usage_records", None)
    if usage_records is None:
        usage_records = []
        request.app.state.usage_records = usage_records
    usage_records.append(usage)
