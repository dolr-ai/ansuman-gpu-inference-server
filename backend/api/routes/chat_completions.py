"""Chat completion routes."""

import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from backend.api.deps import VLLMClientDep
from backend.schemas.chat_completion import ChatCompletionRequest
from backend.services.vllm.client import VLLMClient
from backend.services.vllm.errors import VLLMError, VLLMTimeoutError, VLLMUpstreamError

router = APIRouter(prefix="/v1/chat", tags=["chat"])


@router.post("/completions", response_model=None)
async def create_chat_completion(
    request: ChatCompletionRequest,
    vllm_client: VLLMClientDep,
) -> dict[str, Any] | StreamingResponse | JSONResponse:
    """Forward OpenAI-compatible chat completion requests to vLLM."""
    payload = request.to_vllm_payload()

    if request.stream:
        return StreamingResponse(
            _stream_vllm_response(vllm_client, payload),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache, no-transform"},
        )

    try:
        return await vllm_client.chat_completion(payload)
    except VLLMError as exc:
        return _vllm_error_response(exc)


async def _stream_vllm_response(
    vllm_client: VLLMClient,
    payload: dict[str, Any],
) -> AsyncIterator[bytes]:
    try:
        async for chunk in vllm_client.stream_chat_completion(payload):
            yield chunk
    except VLLMError as exc:
        yield _format_sse_error(exc)
        yield b"data: [DONE]\n\n"


def _vllm_error_response(exc: VLLMError) -> JSONResponse:
    status_code = _status_code_for_vllm_error(exc)
    code = "upstream_timeout" if isinstance(exc, VLLMTimeoutError) else "upstream_error"
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": str(exc),
                "type": code,
                "code": code,
            }
        },
    )


def _format_sse_error(exc: VLLMError) -> bytes:
    code = "upstream_timeout" if isinstance(exc, VLLMTimeoutError) else "upstream_error"
    data = {"error": {"message": str(exc), "code": code}}
    return f"data: {json.dumps(data)}\n\n".encode()


def _status_code_for_vllm_error(exc: VLLMError) -> int:
    if isinstance(exc, VLLMTimeoutError):
        return 504
    if isinstance(exc, VLLMUpstreamError) and exc.status_code and exc.status_code < 500:
        return exc.status_code
    return 502
