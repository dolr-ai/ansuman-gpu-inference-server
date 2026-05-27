"""vLLM HTTP client."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from backend.services.vllm.errors import VLLMTimeoutError, VLLMUpstreamError


class VLLMClient:
    """Small async adapter for vLLM's OpenAI-compatible API."""

    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds)

    async def chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                response = await client.post("/v1/chat/completions", json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc:
            raise VLLMTimeoutError("vLLM request timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise VLLMUpstreamError(
                "vLLM returned an error response",
                status_code=exc.response.status_code,
            ) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise VLLMUpstreamError("vLLM request failed") from exc

    async def stream_chat_completion(self, payload: dict[str, Any]) -> AsyncIterator[bytes]:
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                async with client.stream("POST", "/v1/chat/completions", json=payload) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        if chunk:
                            yield chunk
        except httpx.TimeoutException as exc:
            raise VLLMTimeoutError("vLLM stream timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise VLLMUpstreamError(
                "vLLM returned an error response",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise VLLMUpstreamError("vLLM stream failed") from exc
