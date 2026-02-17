"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe config with .env file support.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./avenir.db"

    # JWT
    SECRET_KEY: str = "avenir-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Overpass API
    OVERPASS_API_URL: str = "https://overpass-api.de/api/interpreter"
    CACHE_TTL_HOURS: int = 24  # Cache infrastructure data for 24 hours

    # Gemini AI
    GEMINI_API_KEY: str = "AIzaSyB8II1Wt3lYvTPCFX0MAvWRpI4JTJYhaHc"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
