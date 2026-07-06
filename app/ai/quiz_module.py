"""Quiz generation module using Gemini."""
import json
import re

from app.ai.gemini_client import gemini_client
from app.prompts.prompts import QUIZ_PROMPT
from app.utils.text_processing import clean_text


class QuizModule:
    async def generate(
        self,
        topic: str,
        difficulty: str = "medium",
        num_questions: int = 5,
        api_key: str | None = None,
    ) -> tuple[list[dict], str]:
        topic = clean_text(topic)
        difficulty = difficulty.lower()
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"

        prompt = QUIZ_PROMPT.format(
            topic=topic, difficulty=difficulty, num_questions=num_questions
        )

        client = gemini_client
        if api_key:
            from app.ai.gemini_client import GeminiClient
            client = GeminiClient(api_key)

        raw = await client.generate(prompt)
        questions = self._parse_json(raw)
        return questions[:num_questions], "Gemini 1.5 Pro"

    def _parse_json(self, text: str) -> list[dict]:
        # Try to extract JSON array from response
        match = re.search(r"\[[\s\S]*\]", text)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, list):
                    return [self._normalize_q(q) for q in data]
            except json.JSONDecodeError:
                pass
        return [self._fallback_question(text)]

    def _normalize_q(self, q: dict) -> dict:
        return {
            "question": q.get("question", ""),
            "option_a": q.get("option_a", q.get("optionA", "")),
            "option_b": q.get("option_b", q.get("optionB", "")),
            "option_c": q.get("option_c", q.get("optionC", "")),
            "option_d": q.get("option_d", q.get("optionD", "")),
            "correct_option": q.get("correct_option", q.get("correctOption", "A")).upper(),
            "explanation": q.get("explanation", ""),
        }

    def _fallback_question(self, text: str) -> dict:
        return {
            "question": "Sample question from generated content",
            "option_a": "Option A",
            "option_b": "Option B",
            "option_c": "Option C",
            "option_d": "Option D",
            "correct_option": "A",
            "explanation": text[:200],
        }


quiz_module = QuizModule()
