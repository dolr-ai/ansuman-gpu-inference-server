"""Application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/gpu_inference",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    rate_limit_rpm: int = Field(default=60, alias="RATE_LIMIT_RPM")
    concurrent_request_limit: int = Field(default=4, alias="CONCURRENT_REQUEST_LIMIT")
    clickhouse_url: str = Field(default="http://localhost:8123", alias="CLICKHOUSE_URL")
    vllm_base_url: str = Field(default="http://localhost:8001", alias="VLLM_BASE_URL")
    model_ids_raw: str = Field(default="test-model", alias="MODEL_IDS")
    api_key_prefix: str = Field(default="an", alias="API_KEY_PREFIX")
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")
    sentry_send_default_pii: bool = Field(default=False, alias="SENTRY_SEND_DEFAULT_PII")
    service_name: str = Field(default="gpu-inference-backend", alias="SERVICE_NAME")
    release: str | None = Field(default=None, alias="RELEASE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def model_ids(self) -> tuple[str, ...]:
        """Configured public model identifiers."""
        return tuple(
            model_id.strip() for model_id in self.model_ids_raw.split(",") if model_id.strip()
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings for application runtime."""
    return Settings()
