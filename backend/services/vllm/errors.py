"""vLLM error mapping."""

import httpx

from backend.core.errors import AppError


def timeout_error(exc: httpx.TimeoutException) -> AppError:
    """Map an upstream timeout to the public API error contract."""
    return AppError(
        message="vLLM upstream timed out",
        code="upstream_timeout",
        status_code=504,
        type="server_error",
    )


def upstream_status_error(status_code: int) -> AppError:
    """Map an unexpected upstream HTTP status to the public API error contract."""
    return AppError(
        message=f"vLLM upstream returned HTTP {status_code}",
        code="upstream_error",
        status_code=502,
        type="server_error",
    )


def invalid_response_error() -> AppError:
    """Map malformed upstream responses to the public API error contract."""
    return AppError(
        message="vLLM upstream returned an invalid response",
        code="upstream_invalid_response",
        status_code=502,
        type="server_error",
    )
