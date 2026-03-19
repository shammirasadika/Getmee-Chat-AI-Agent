
import os
import httpx
from app.core.prompts import SYSTEM_PROMPT, TRANSLATION_SYSTEM_PROMPT, LANGUAGE_CLEANUP_PROMPT

class LLMClient:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key

    async def generate(self, prompt: str, language: str = "en") -> str:
        if self.provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT.format(language=language)},
                    {"role": "user", "content": prompt}
                ]
            }
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return content
            except Exception as e:
                print(f"[Groq API Error] {e}", flush=True)
                return f"Sorry, I was unable to generate a response. Error: {e}"
        return f"[LLM error: Provider '{self.provider}' is not supported. Set LLM_PROVIDER=groq in your .env file.]"

    async def translate(self, text: str, target_language: str) -> str:
        """Translate text to the target language using the LLM."""
        if self.provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT.format(target_language=target_language)},
                    {"role": "user", "content": text}
                ]
            }
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"[Groq Translation Error] {e}", flush=True)
                return text  # Return original text if translation fails
        return text

    async def cleanup_language(self, text: str, language: str) -> str:
        """Rewrite text to ensure it is entirely in the target language."""
        if self.provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": LANGUAGE_CLEANUP_PROMPT.format(language=language)},
                    {"role": "user", "content": text}
                ]
            }
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"[Groq Cleanup Error] {e}", flush=True)
                return text
        return text
