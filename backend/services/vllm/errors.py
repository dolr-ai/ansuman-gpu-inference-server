"""vLLM error mapping."""


class VLLMError(Exception):
    """Base error for upstream vLLM failures."""


class VLLMTimeoutError(VLLMError):
    """Raised when vLLM does not respond before the configured timeout."""


class VLLMUpstreamError(VLLMError):
    """Raised when vLLM returns an error response or cannot be reached."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
