from datetime import datetime
from pydantic import BaseModel

class NoteCreate(BaseModel):
    title : str
    content : str


class NoteUpdate(BaseModel):
    title : str
    content : str


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