"""Integration tests for health routes."""

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-request-id"].startswith("req_")


def test_request_id_header_is_preserved(client: TestClient) -> None:
    response = client.get("/health", headers={"x-request-id": "req_external"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req_external"
