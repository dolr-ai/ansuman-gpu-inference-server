"""ID generation helpers."""

from uuid import uuid4


def generate_request_id() -> str:
    """Create a compact request ID for logs and response headers."""
    return f"req_{uuid4().hex}"
