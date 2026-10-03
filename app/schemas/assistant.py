from pydantic import BaseModel , field_validator
from app.schemas.rag import RAGResult

class AssistantChatRequest(BaseModel):
    conversation_id : int
    message : str

    @field_validator("message")
    @classmethod
    def validate_message(cls , value : str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty")

        return value


class AssistantSource(BaseModel):
     note_id: int
     chunk_id: int
     chunk_index: int
     content: str

class AssistantChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    answer: str
    sources: list[AssistantSource]

class AssistantServiceResult(BaseModel):
    message_id: int
    rag_result: RAGResult
