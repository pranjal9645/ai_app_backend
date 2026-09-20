from datetime import datetime
from pydantic import BaseModel , Field , field_validator

class NoteCreate(BaseModel):
    title : str = Field(min_length=1 , max_length=255)
    content : str = Field(min_length=1)

    @field_validator("title" , "content")
    @classmethod
    def validate_not_blank(cls , value : str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field Cannot be blank")

        return value

class NoteUpdate(BaseModel):
    title : str = Field(min_length=1 , max_length=255)
    content : str = Field(min_length=1)


    @field_validator("title" , "content")
    @classmethod
    def validate_not_blank(cls , value : str) -> str:
            value = value.strip()
    
            if not value:
                raise ValueError("Field Cannot be blank")
    
            return value


class NoteResponse(BaseModel):
    id : int
    title : str
    content: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
         "from_attributes": True
    }

class NoteListResponse(BaseModel):
    items : list[NoteResponse]
    total : int
    skip : int
    limit : int
    has_more : bool


class SemanticSearchItem(BaseModel):
    note_id: int
    chunk_id: int
    chunk_index: int
    content: str
    distance: float


class SemanticSearchResponse(BaseModel):
    items: list[SemanticSearchItem]
    query: str
    limit: int