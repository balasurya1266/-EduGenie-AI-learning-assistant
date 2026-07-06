"""Flashcard generation module."""
import json
import re

from app.ai.gemini_client import gemini_client
from app.prompts.prompts import FLASHCARD_PROMPT


class FlashcardModule:
    async def generate(self, topic: str, num_cards: int = 10, api_key: str | None = None) -> list[dict]:
        prompt = FLASHCARD_PROMPT.format(topic=topic, num_cards=num_cards)
        client = gemini_client
        if api_key:
            from app.ai.gemini_client import GeminiClient
            client = GeminiClient(api_key)

        raw = await client.generate(prompt)
        match = re.search(r"\[[\s\S]*\]", raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return [{"front": topic, "back": raw[:300]}]


flashcard_module = FlashcardModule()
