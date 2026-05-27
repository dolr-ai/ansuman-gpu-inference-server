"""Tests for application settings."""

from pytest import MonkeyPatch

from backend.core.config import Settings


def test_settings_defaults_to_local_vllm(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("VLLM_BASE_URL", raising=False)
    monkeypatch.delenv("VLLM_MODEL", raising=False)
    settings = Settings(_env_file=None)

    assert settings.vllm_base_url == "http://127.0.0.1:8001"
    assert settings.vllm_model == "yral-gpu-inference"
