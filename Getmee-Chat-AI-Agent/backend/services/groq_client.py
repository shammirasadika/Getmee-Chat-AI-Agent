from groq import Groq
from configuration.settings import settings


class GroqClient:
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")

        self.client = Groq(api_key=settings.groq_api_key)

    def chat(self, message: str):
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content