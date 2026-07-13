"""Summarization module using Gemini."""
from app.ai.gemini_client import gemini_client
from app.prompts.prompts import SUMMARY_FORMAT, SUMMARY_PROMPTS
from app.utils.text_processing import clean_text, truncate


class SummaryModule:
    async def summarize(
        self,
        text: str,
        summary_type: str = "medium",
        api_key: str | None = None,
    ) -> tuple[str, str]:
        text = clean_text(text)
        if len(text) > 15000:
            text = truncate(text, 15000)

        stype = summary_type.lower()
        instruction = SUMMARY_PROMPTS.get(stype, SUMMARY_PROMPTS["medium"])
        prompt = SUMMARY_FORMAT.format(instruction=instruction, text=text)

        client = gemini_client
        if api_key:
            from app.ai.gemini_client import GeminiClient
            client = GeminiClient(api_key)

        response = await client.generate(prompt)
        return response, "Gemini 1.5 Pro"


summary_module = SummaryModule()
