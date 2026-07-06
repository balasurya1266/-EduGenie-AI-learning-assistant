"""Learning path generation module using Gemini."""
from app.ai.gemini_client import gemini_client
from app.prompts.prompts import LEARNING_PATH_PROMPT
from app.utils.text_processing import clean_text


class LearningPathModule:
    async def generate(
        self,
        topic: str,
        current_level: str,
        weekly_hours: int,
        goal: str,
        api_key: str | None = None,
    ) -> tuple[str, str]:
        topic = clean_text(topic)
        goal = clean_text(goal)
        prompt = LEARNING_PATH_PROMPT.format(
            topic=topic,
            current_level=current_level,
            weekly_hours=weekly_hours,
            goal=goal,
        )

        client = gemini_client
        if api_key:
            from app.ai.gemini_client import GeminiClient
            client = GeminiClient(api_key)

        response = await client.generate(prompt)
        return response, "Gemini 1.5 Pro"


learning_path_module = LearningPathModule()
