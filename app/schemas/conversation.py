from pydantic import BaseModel , field_validator
from typing import Literal
from datetime import datetime
from app.schemas.rag import RAGSource

class ConversationTurn(BaseModel):
    role : Literal["user" , "assistant"]
    content : str

    @field_validator("content")
    @classmethod
    def validate_content(cls , value : str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message content cannot be empty")

        return value


class ConversationContext(BaseModel):
    history : list[ConversationTurn]
    current_message : str

    @field_validator("current_message")
    @classmethod
    def validate_current_message(cls , value : str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Current message cannot be Empty")


        return value


class RewrittenQuery(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Rewritten query cannot be empty")

        return value

class ConversationCreateRequest(BaseModel):
        title : str | None = None

        @field_validator("title")
        @classmethod
        def validate_title(cls , value : str | None) -> str | None:
            if value is None:
                return None

            value = value.strip()

            if not value:
                return None

            if len(value) > 255:
                raise ValueError(
                    "Conversation title cannot exceed 255 characters"
                )

            return value


class ConversationResponse(BaseModel):
    id: int
    title: str | None
    created_at: datetime
    updated_at: datetime

class ConversationMessageRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Message cannot be empty"
            )

        return value


class ConversationMessageResponse(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class ConversationChatResponse(BaseModel):
    conversation_id: int
    answer: str
    sources: list[RAGSource]

class MessageCursor(BaseModel):
    created_at : datetime
    id : int


class PaginatedConversationMessagesResponse(BaseModel):
    items : list[ConversationMessageResponse]
    next_cursor : MessageCursor | None
    has_more : bool