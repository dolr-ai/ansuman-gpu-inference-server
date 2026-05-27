"""Integration tests for non-streaming chat completions."""

from typing import Any

from fastapi.testclient import TestClient

from backend.api.deps import get_vllm_client
from backend.main import app


class FakeVLLMClient:
    def __init__(self) -> None:
        self.payload: dict[str, Any] | None = None

    async def chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payload = payload
        return {
            "id": "chatcmpl_test",
            "object": "chat.completion",
            "model": payload["model"],
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "pong"},
                    "finish_reason": "stop",
                }
            ],
        }


def test_chat_completion_forwards_payload(client: TestClient) -> None:
    fake_client = FakeVLLMClient()
    app.dependency_overrides[get_vllm_client] = lambda: fake_client

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "yral-gpu-inference",
            "messages": [{"role": "user", "content": "ping"}],
            "temperature": 0,
        },
    )

    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "pong"
    assert fake_client.payload == {
        "model": "yral-gpu-inference",
        "messages": [{"role": "user", "content": "ping"}],
        "stream": False,
        "temperature": 0.0,
    }


def test_chat_completion_validates_messages(client: TestClient) -> None:
    response = client.post(
        "/v1/chat/completions",
        json={"model": "yral-gpu-inference", "messages": []},
    )

    assert response.status_code == 422
