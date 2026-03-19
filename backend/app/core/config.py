import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "../ingestion_pipeline/chroma-data")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/getmee")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
