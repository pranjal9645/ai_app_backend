import ollama
from app.core.config import settings

class LLMService:

    def __init__(self):
        self.model = settings.llm_model

    def generate(self , system_prompt : str , user_prompt : str) -> str:
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