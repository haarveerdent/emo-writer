import os
from openai import OpenAI
from pipeline.config import OPENAI_MODEL


class OpenAIResponsesClient:
    """
    Wraps the OpenAI Responses API (v1/responses).
    Uses client.responses.create(), NOT client.chat.completions.create().
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = OPENAI_MODEL

    def call(self, system_prompt: str, user_message: str, temperature: float = 0.0) -> str:
        # gpt-5-nano does not support the temperature parameter via the Responses API
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_message,
        )
        return response.output_text
