"""Tests for application configuration."""

from backend.core.config import Settings


def test_settings_load_from_env(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.1:8001")

    settings = Settings()

    assert settings.app_env == "test"
    assert settings.log_level == "DEBUG"
    assert settings.vllm_base_url == "http://127.0.0.1:8001"


def test_settings_parses_model_ids() -> None:
    settings = Settings(model_ids_raw="model-a, model-b,,")

    assert settings.model_ids == ("model-a", "model-b")
