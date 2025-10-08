import os
import logging
import httpx
from typing import Protocol
from openai import OpenAI


logger = logging.getLogger(__name__)


class AIProvider(Protocol):
    def generate(self, prompt: str, model: str) -> str: ...


class OpenRouterProvider:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not key:
            logger.critical("CRITICAL: OPENROUTER_API_KEY not found. The application cannot start without it.")
            raise SystemExit("OPENROUTER_API_KEY not set.")
        self.client = OpenAI(
            base_url=base_url or "https://openrouter.ai/api/v1",
            api_key=key,
            default_headers={
                "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:3000"),
                "X-Title": os.getenv("APP_TITLE", "Legal Analyser"),
            },
        )

    def generate(self, prompt: str, model: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            if not response or not response.choices:
                raise ValueError("Empty response from OpenRouter")
            return response.choices[0].message.content.strip()
        except httpx.RequestError as e:
            logger.error(f"OpenRouter API request failed: {e}")
            raise Exception("API request failed. Please try again later.")
        except Exception:
            raise


