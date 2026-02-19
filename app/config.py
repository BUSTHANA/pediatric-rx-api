"""
Application configuration.
Loads environment variables and provides a central config object.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    APP_NAME: str = "Pediatric Medicine AI"
    APP_VERSION: str = "1.0.0"

    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
