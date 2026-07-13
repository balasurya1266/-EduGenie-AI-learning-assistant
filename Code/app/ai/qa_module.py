"""Question Answering module using Gemini."""
from typing import AsyncGenerator, Optional

from app.ai.gemini_client import gemini_client
from app.prompts.prompts import QA_SYSTEM
from app.utils.text_processing import clean_text


class QAModule:
    async def answer(
        self,
        question: str,
        user_id: str,
        api_key: Optional[str] = None,
    ) -> tuple[str, str]:
        question = clean_text(question)
        client = gemini_client
        if api_key:
            from app.ai.gemini_client import GeminiClient
            client = GeminiClient(api_key)

        response = await client.generate(question, system=QA_SYSTEM)
        return response, "Gemini"

    async def stream_answer(
        self,
        question: str,
        user_id: str,
        api_key: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        question = clean_text(question)
        client = gemini_client
        if api_key:
            from app.ai.gemini_client import GeminiClient
            client = GeminiClient(api_key)

        async for chunk in client.stream(question, system=QA_SYSTEM):
            yield chunk


qa_module = QAModule()
