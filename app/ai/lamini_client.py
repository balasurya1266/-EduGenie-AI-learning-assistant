"""LaMini-Flan-T5 local model client with Gemini fallback."""
import asyncio
from typing import Optional

from app.ai.gemini_client import gemini_client
from app.config import LAMINI_MODEL, USE_LOCAL_LAMINI
from app.prompts.prompts import EXPLAIN_PROMPT


class LaMiniClient:
    def __init__(self):
        self._pipeline = None
        self._loaded = False
        self._load_error: Optional[str] = None

    def _try_load(self) -> bool:
        if self._loaded:
            return self._pipeline is not None
        if not USE_LOCAL_LAMINI:
            self._load_error = "Local LaMini disabled. Set USE_LOCAL_LAMINI=true to enable."
            self._loaded = True
            return False
        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                "text2text-generation",
                model=LAMINI_MODEL,
                max_length=512,
            )
            self._loaded = True
            return True
        except Exception as e:
            self._load_error = str(e)
            self._loaded = True
            return False

    async def explain(self, topic: str, level: str = "beginner") -> tuple[str, str]:
        prompt = EXPLAIN_PROMPT.format(topic=topic, level=level)

        if self._try_load() and self._pipeline:
            loop = asyncio.get_event_loop()

            def _generate():
                result = self._pipeline(
                    f"Explain {topic} for a {level} student in simple terms with examples.",
                    max_length=512,
                    do_sample=False,
                )
                return result[0]["generated_text"]

            text = await loop.run_in_executor(None, _generate)
            return text, "LaMini-Flan-T5"

        # Fallback to Gemini
        text = await gemini_client.generate(prompt)
        return text, "Gemini 1.5 Pro (LaMini fallback)"


lamini_client = LaMiniClient()
