"""Batch worker entrypoint."""

import asyncio

from backend.core.config import get_settings
from backend.services.observability.sentry import capture_exception, initialize_sentry


async def main() -> None:
    settings = get_settings()
    initialize_sentry(settings)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        capture_exception(exc, tags={"component": "batch_worker"})
        raise
