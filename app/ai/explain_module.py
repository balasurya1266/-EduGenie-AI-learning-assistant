"""Concept explanation module using LaMini-Flan-T5."""
from app.ai.lamini_client import lamini_client
from app.utils.text_processing import clean_text


class ExplainModule:
    async def explain(self, topic: str, level: str = "beginner") -> tuple[str, str]:
        topic = clean_text(topic)
        level = level.lower()
        if level not in ("beginner", "intermediate", "advanced"):
            level = "beginner"
        return await lamini_client.explain(topic, level)


explain_module = ExplainModule()
