"""Google Gemini API client with streaming support."""
import asyncio
from typing import AsyncGenerator, Optional

import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self._configured = False
        self._model = None

    def _ensure_configured(self) -> None:
        if not self.api_key:
            raise ValueError(
                "Gemini API key not configured. Set GEMINI_API_KEY in .env or Settings."
            )
        if not self._configured:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(GEMINI_MODEL)
            self._configured = True

    async def generate(self, prompt: str, system: str = "") -> str:
        self._ensure_configured()
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: self._model.generate_content(full_prompt)
        )
        return response.text or ""

    async def stream(self, prompt: str, system: str = "") -> AsyncGenerator[str, None]:
        self._ensure_configured()
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        loop = asyncio.get_event_loop()

        def _stream():
            return self._model.generate_content(full_prompt, stream=True)

        response = await loop.run_in_executor(None, _stream)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    async def embed(self, text: str) -> list[float]:
        self._ensure_configured()
        loop = asyncio.get_event_loop()

        def _embed():
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document",
            )
            return result["embedding"]

        return await loop.run_in_executor(None, _embed)


gemini_client = GeminiClient()
