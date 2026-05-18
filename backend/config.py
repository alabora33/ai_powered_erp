"""
Application configuration using Pydantic Settings.
All settings are loaded from environment variables or .env file.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────────
    app_name: str = "AI ERP - Excel Data Mapper"
    app_version: str = "1.0.0"
    environment: str = Field(default="development")
    secret_key: str = Field(default="change-me-in-production")
    log_level: str = Field(default="INFO")

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://erp_user:erp_password@localhost:5432/ai_erp"
    )
    database_url_sync: str = Field(
        default="postgresql://erp_user:erp_password@localhost:5432/ai_erp"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # ── Redis / Celery ─────────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/1")

    # ── AI / Gemini ───────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="")
    gemini_model: str = "gemini-1.5-flash"

    # ── File Upload ───────────────────────────────────────────────────────────
    upload_dir: str = "/app/uploads"
    max_file_size_mb: int = 50
    allowed_extensions: list[str] = [".xlsx", ".xls", ".csv"]

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins: list[str] = ["*"]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
