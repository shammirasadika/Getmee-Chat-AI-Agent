import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # App config
    app_name: str = "GetMee Chat Backend"
    app_version: str = "1.0.0"
    debug: bool = True

    # LLM config
    llm_provider: str = "groq"
    groq_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()