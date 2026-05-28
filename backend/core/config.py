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
    token_limit_tpm: int = Field(default=60_000, alias="TOKEN_LIMIT_TPM")
    max_input_tokens: int = Field(default=8_192, alias="MAX_INPUT_TOKENS")
    max_output_tokens: int = Field(default=2_048, alias="MAX_OUTPUT_TOKENS")
    max_total_tokens: int = Field(default=10_240, alias="MAX_TOTAL_TOKENS")
    clickhouse_url: str = Field(default="http://localhost:8123", alias="CLICKHOUSE_URL")
    clickhouse_database: str = Field(default="yral", alias="CLICKHOUSE_DATABASE")
    clickhouse_user: str = Field(default="default", alias="CLICKHOUSE_USER")
    clickhouse_password: str = Field(default="", alias="CLICKHOUSE_PASSWORD")
    clickhouse_secure: bool = Field(default=False, alias="CLICKHOUSE_SECURE")
    clickhouse_verify: bool = Field(default=True, alias="CLICKHOUSE_VERIFY")
    clickhouse_cluster: str = Field(default="default", alias="CLICKHOUSE_CLUSTER")
    analytics_queue_size: int = Field(default=1000, alias="ANALYTICS_QUEUE_SIZE")
    analytics_flush_batch_size: int = Field(default=500, alias="ANALYTICS_FLUSH_BATCH_SIZE")
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
