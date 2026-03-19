from configuration.settings import settings
from services.groq_client import GroqClient
from services.mock_client import MockClient


def get_ai_client():
    if settings.llm_provider.lower() == "groq":
        return GroqClient()

    elif settings.llm_provider.lower() == "mock":
        return MockClient()

    else:
        raise ValueError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )