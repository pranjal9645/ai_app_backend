from pydantic import BaseModel , field_validator
from typing import Literal

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


