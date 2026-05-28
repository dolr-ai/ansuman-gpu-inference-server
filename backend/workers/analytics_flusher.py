"""Analytics flusher worker entrypoint."""

import asyncio

from backend.core.config import get_settings
from backend.db.clickhouse import ClickHouseClient
from backend.services.observability.sentry import capture_exception, initialize_sentry
from backend.services.analytics.clickhouse_flusher import ClickHouseFlusher
from backend.services.analytics.event_collector import AnalyticsCollector


async def main() -> None:
    settings = get_settings()
    initialize_sentry(settings)
    collector = AnalyticsCollector(max_size=settings.analytics_queue_size)
    client = ClickHouseClient.from_settings(
        url=settings.clickhouse_url,
        database=settings.clickhouse_database,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
        secure=settings.clickhouse_secure,
        verify=settings.clickhouse_verify,
    )
    flusher = ClickHouseFlusher(
        collector=collector,
        client=client,
        batch_size=settings.analytics_flush_batch_size,
    )
    await flusher.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        capture_exception(exc, tags={"component": "analytics_flusher"})
        raise
