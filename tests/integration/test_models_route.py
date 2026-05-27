"""Integration tests for model routes."""

from fastapi.testclient import TestClient

from backend.core.config import Settings, get_settings
from backend.main import app


def test_models_returns_configured_model(client: TestClient) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        vllm_model="test-model",
    )

    response = client.get("/v1/models")

    assert response.status_code == 200
    assert response.json() == {
        "object": "list",
        "data": [
            {
                "id": "test-model",
                "object": "model",
                "created": 0,
                "owned_by": "yral",
            }
        ],
    }
