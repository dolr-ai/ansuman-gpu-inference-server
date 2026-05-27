"""Tests for application import wiring."""

from backend.main import app


def test_app_imports() -> None:
    assert app.title == "GPU Inference Backend"


def test_phase_one_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/health" in paths
    assert "/v1/models" in paths
    assert "/v1/chat/completions" in paths
