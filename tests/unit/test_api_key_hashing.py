"""Tests for API key hashing."""

import pytest

from backend.core.errors import AppError
from backend.services.auth.api_key_service import (
    AuthContext,
    StaticApiKeyAuthService,
    ensure_model_allowed,
    generate_api_key,
)
from backend.services.auth.password_hashing import hash_api_key, key_debug_prefix


def test_raw_api_key_hashing_is_stable_and_not_plaintext() -> None:
    raw_key = "an_test_secret"

    hashed = hash_api_key(raw_key)

    assert hashed == hash_api_key(raw_key)
    assert hashed != raw_key
    assert len(hashed) == 64


def test_key_generation_uses_yral_prefix() -> None:
    raw_key = generate_api_key("an")

    assert raw_key.startswith("an_")
    assert key_debug_prefix(raw_key) == raw_key[:16]


def test_invalid_key_returns_401_error() -> None:
    service = StaticApiKeyAuthService({})

    async def scenario() -> None:
        await service.authenticate("an_missing")

    import asyncio

    with pytest.raises(AppError) as exc_info:
        asyncio.run(scenario())

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "invalid_api_key"


def test_disallowed_model_returns_403_error() -> None:
    auth_context = AuthContext(
        api_key_id="key_test",
        user_id="user_test",
        project_id="project_test",
        allowed_models=("allowed-model",),
    )

    with pytest.raises(AppError) as exc_info:
        ensure_model_allowed(auth_context, "blocked-model")

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "model_not_allowed"
