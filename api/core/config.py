"""
core/config.py — Environment-based configuration using pydantic-settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service
    app_name: str = "Instruction Clarity Agent"
    app_version: str = "1.0.0"
    debug: bool = False

    # Gemini
    gemini_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — reads from environment / .env once."""
    return Settings()
