import os
from pathlib import Path
from dotenv import dotenv_values

SUPPORTED_LLM_PROVIDERS = ["groq"]

# Load .env values directly (bypasses any system env vars)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
env_vars = dotenv_values(env_path)

def get_config(key: str, default: str = "") -> str:
    """Get config value: .env file takes priority, then os.environ, then default."""
    return env_vars.get(key, os.getenv(key, default))

class Settings:
    CHROMA_PATH: str = get_config("CHROMA_PATH", "../ingestion_pipeline/chroma-data")
    REDIS_URL: str = get_config("REDIS_URL", "redis://localhost:6379/0")
    POSTGRES_URL: str = get_config("POSTGRES_URL", "postgresql://user:password@localhost:5432/getmee")
    LLM_PROVIDER: str = get_config("LLM_PROVIDER", "groq")
    LLM_API_KEY: str = get_config("LLM_API_KEY", get_config("GROQ_API_KEY", ""))
    LOG_LEVEL: str = get_config("LOG_LEVEL", "INFO")
    ALLOW_GENERAL_FALLBACK: bool = get_config("ALLOW_GENERAL_FALLBACK", "true").lower() == "true"

settings = Settings()

# Startup validation
if settings.LLM_PROVIDER not in SUPPORTED_LLM_PROVIDERS:
    raise RuntimeError(
        f"[CONFIG ERROR] LLM_PROVIDER='{settings.LLM_PROVIDER}' is not supported. "
        f"Supported providers: {SUPPORTED_LLM_PROVIDERS}. "
        f"Check your .env file for duplicate LLM_PROVIDER entries."
    )
if not settings.LLM_API_KEY:
    raise RuntimeError(
        "[CONFIG ERROR] GROQ_API_KEY / LLM_API_KEY is not set. "
        "Add GROQ_API_KEY=your_key to your .env file."
    )

print(f"[CONFIG] LLM_PROVIDER={settings.LLM_PROVIDER}, LLM_API_KEY=set", flush=True)
