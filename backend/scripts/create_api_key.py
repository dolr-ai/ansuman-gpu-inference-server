"""Create an API key and print the raw key once."""

import argparse
import asyncio
from datetime import UTC, datetime

from backend.core.config import get_settings
from backend.db.postgres import create_postgres_engine, create_sessionmaker
from backend.repositories.api_key_repository import ApiKeyRepository
from backend.services.auth.api_key_service import ApiKeyService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a gpu-inference API key")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument(
        "--allowed-model",
        action="append",
        dest="allowed_models",
        help="Allowed model ID. Repeat for multiple models. Omit to allow all models.",
    )
    parser.add_argument(
        "--expires-at",
        help="Optional ISO-8601 UTC timestamp, for example 2026-06-30T00:00:00+00:00.",
    )
    return parser.parse_args()


def parse_expires_at(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


async def main() -> None:
    args = parse_args()
    settings = get_settings()
    engine = create_postgres_engine(settings.database_url)
    try:
        service = ApiKeyService(
            ApiKeyRepository,
            create_sessionmaker(engine),
            key_prefix=settings.api_key_prefix,
        )
        created = await service.create_api_key(
            user_id=args.user_id,
            project_id=args.project_id,
            name=args.name,
            allowed_models=args.allowed_models,
            expires_at=parse_expires_at(args.expires_at),
        )
    finally:
        await engine.dispose()

    print(f"api_key_id={created.api_key_id}")
    print(f"key_prefix={created.key_prefix}")
    print(f"raw_key={created.raw_key}")


if __name__ == "__main__":
    asyncio.run(main())
