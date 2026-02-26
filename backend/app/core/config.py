"""
Application configuration loaded from environment variables.
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Default SQLite file in backend folder so it works regardless of CWD
_DEFAULT_SQLITE_PATH = Path(__file__).resolve().parent.parent / "ticketnew.db"


class Settings(BaseSettings):
    """Application settings from environment."""

    # App
    APP_NAME: str = "Ticket Agent API"
    DEBUG: bool = False

    # Database (use SQLite by default for local dev; set to PostgreSQL URL for production)
    DATABASE_URL: str = f"sqlite:///{_DEFAULT_SQLITE_PATH.as_posix()}"

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
