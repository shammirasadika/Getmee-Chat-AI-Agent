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
    CHROMA_MODE: str = get_config("CHROMA_MODE")
    CHROMA_HOST: str = get_config("CHROMA_HOST")
    CHROMA_PORT: int = int(get_config("CHROMA_PORT"))
    CHROMA_PATH: str = get_config("CHROMA_PATH")
    CHROMA_COLLECTION: str = get_config("CHROMA_COLLECTION")  
    REDIS_URL: str = get_config("REDIS_URL")
    POSTGRES_URL: str = get_config("POSTGRES_URL")
    LLM_PROVIDER: str = get_config("LLM_PROVIDER")
    LLM_API_KEY: str = get_config("LLM_API_KEY")
    LOG_LEVEL: str = get_config("LOG_LEVEL")
    ALLOW_GENERAL_FALLBACK: bool = get_config("ALLOW_GENERAL_FALLBACK", "false").lower() == "true"
    SUPPORT_EMAIL: str = get_config("SUPPORT_EMAIL")
    SUPPORT_EMAIL_COOLDOWN: int = int(get_config("SUPPORT_EMAIL_COOLDOWN", "300"))
    ALLOWED_ORIGINS: list = [o.strip() for o in get_config("ALLOWED_ORIGINS", "").split(",") if o.strip()]
    PORT: int = int(get_config("PORT"))

    # Email settings
    MAIL_USERNAME: str = get_config("MAIL_USERNAME")
    MAIL_PASSWORD: str = get_config("MAIL_PASSWORD")
    MAIL_FROM: str = get_config("MAIL_FROM")
    MAIL_PORT: int = int(get_config("MAIL_PORT"))
    MAIL_SERVER: str = get_config("MAIL_SERVER")
    MAIL_STARTTLS: bool = get_config("MAIL_STARTTLS", get_config("MAIL_TLS", "True")) == "True"
    MAIL_SSL_TLS: bool = get_config("MAIL_SSL_TLS", get_config("MAIL_SSL", "False")) == "True"

settings = Settings()

# Startup validation for required ChromaDB collection
if not settings.CHROMA_COLLECTION:
    raise RuntimeError(
        "[CONFIG ERROR] CHROMA_COLLECTION is not set. "
        "Add CHROMA_COLLECTION=your_collection_name to your .env file."
    )

# Startup validation
if settings.LLM_PROVIDER not in SUPPORTED_LLM_PROVIDERS:
    raise RuntimeError(
        f"[CONFIG ERROR] LLM_PROVIDER='{settings.LLM_PROVIDER}' is not supported. "
        f"Supported providers: {SUPPORTED_LLM_PROVIDERS}. "
        f"Check your .env file for duplicate LLM_PROVIDER entries."
    )
if not settings.LLM_API_KEY:
    raise RuntimeError(
        "[CONFIG ERROR] LLM_API_KEY is not set. "
        "Add LLM_API_KEY=your_key to your .env file."
    )
if not settings.REDIS_URL:
    raise RuntimeError(
        "[CONFIG ERROR] REDIS_URL is not set. "
        "Add REDIS_URL=redis://... to your .env file."
    )
if not settings.POSTGRES_URL:
    raise RuntimeError(
        "[CONFIG ERROR] POSTGRES_URL is not set. "
        "Add POSTGRES_URL=postgresql://... to your .env file."
    )


