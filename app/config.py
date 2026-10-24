"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Locate workspace root directory
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class Settings(BaseModel):
    """Application settings typed and defaulted."""

    TELEGRAM_TOKEN: str = Field(
        default_factory=lambda: os.getenv("TELEGRAM_TOKEN", "").strip()
    )
    GEMMA_API_KEY: str = Field(
        default_factory=lambda: os.getenv("GEMMA_API_KEY", "").strip()
    )
    GEMMA_BASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "GEMMA_BASE_URL", "https://openrouter.ai/api/v1"
        ).strip()
    )
    GEMMA_MODEL: str = Field(
        default_factory=lambda: os.getenv(
            "GEMMA_MODEL", "google/gemma-4-31b-it:free"
        ).strip()
    )
    DATABASE_PATH: str = Field(
        default_factory=lambda: os.getenv("DATABASE_PATH", "snapstudy.db").strip()
    )
    LOG_LEVEL: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").strip()
    )
    REQUEST_TIMEOUT_SECONDS: float = Field(
        default_factory=lambda: float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60.0"))
    )
    MAX_IMAGE_SIDE: int = Field(
        default_factory=lambda: int(os.getenv("MAX_IMAGE_SIDE", "1280"))
    )
    MAX_DOWNLOAD_MB: int = Field(
        default_factory=lambda: int(os.getenv("MAX_DOWNLOAD_MB", "10"))
    )
    WEAK_MIN_ATTEMPTS: int = Field(
        default_factory=lambda: int(os.getenv("WEAK_MIN_ATTEMPTS", "2"))
    )
    WEAK_ACCURACY_THRESHOLD: int = Field(
        default_factory=lambda: int(os.getenv("WEAK_ACCURACY_THRESHOLD", "60"))
    )
    PORTAL_BASE_URL: str = Field(
        default_factory=lambda: os.getenv("PORTAL_BASE_URL", "").rstrip("/")
    )
    PORTAL_SECRET: str = Field(
        default_factory=lambda: os.getenv("PORTAL_SECRET", "").strip()
    )
    PORTAL_HOST: str = Field(
        default_factory=lambda: os.getenv("PORTAL_HOST", "127.0.0.1").strip()
    )
    PORTAL_PORT: int = Field(
        default_factory=lambda: int(os.getenv("PORTAL_PORT", "8000"))
    )
    PORTAL_TOKEN_TTL_SECONDS: int = Field(
        default_factory=lambda: int(os.getenv("PORTAL_TOKEN_TTL_SECONDS", "300"))
    )
    PORTAL_SESSION_DAYS: int = Field(
        default_factory=lambda: int(os.getenv("PORTAL_SESSION_DAYS", "7"))
    )
    BOT_USERNAME: str = Field(
        default_factory=lambda: os.getenv("BOT_USERNAME", "").lstrip("@").strip()
    )


settings = Settings()


def reload_settings() -> Settings:
    """Reload settings from .env file."""
    global settings
    load_dotenv(ROOT_DIR / ".env", override=True)
    settings = Settings()
    return settings
