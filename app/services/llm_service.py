import ollama
from app.core.config import settings
from app.core.exceptions import AIServiceUnavailableError

class LLMService:

    def __init__(self):
        self.model = settings.llm_model

    def generate(self , system_prompt : str , user_prompt : str) -> str:
        try:
            response = ollama.chat(model=self.model , messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
        ])

            return response["message"]["content"]

        except (ollama.ResponseError , ConnectionError) as exc:
                raise AIServiceUnavailableError("AI service is currently unavailable") from exc       