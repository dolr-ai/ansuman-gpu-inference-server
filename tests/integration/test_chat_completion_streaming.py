"""Integration tests for streaming chat completions."""

from collections.abc import AsyncIterator
from typing import Any

from fastapi.testclient import TestClient

from backend.api.deps import get_vllm_client
from backend.main import app


class FakeStreamingVLLMClient:
    def __init__(self) -> None:
        self.payload: dict[str, Any] | None = None

    async def stream_chat_completion(self, payload: dict[str, Any]) -> AsyncIterator[bytes]:
        self.payload = payload
        yield b'data: {"choices":[{"delta":{"content":"pong"}}]}\n\n'
        yield b"data: [DONE]\n\n"


def test_streaming_chat_completion_forwards_sse(client: TestClient) -> None:
    fake_client = FakeStreamingVLLMClient()
    app.dependency_overrides[get_vllm_client] = lambda: fake_client

    with client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "yral-gpu-inference",
            "messages": [{"role": "user", "content": "ping"}],
            "stream": True,
        },
    ) as response:
        body = response.read()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert b"pong" in body
    assert body.endswith(b"data: [DONE]\n\n")
    assert fake_client.payload == {
        "model": "yral-gpu-inference",
        "messages": [{"role": "user", "content": "ping"}],
        "stream": True,
    }
