
import os
import httpx

class LLMClient:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key

    async def generate(self, prompt: str, language: str = "en") -> str:
        if self.provider == "groq":
            url = "https://api.groq.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": [
                    {"role": "system", "content": f"Respond in {language}."},
                    {"role": "user", "content": prompt}
                ]
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        # ...existing code for other providers...
        return f"[LLM response in {language} for prompt: {prompt[:30]}...]"
