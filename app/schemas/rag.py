from pydantic import BaseModel , Field

class RetrievedChunk(BaseModel):
    note_id: int
    chunk_id: int
    chunk_index: int
    content: str
    distance: float
    is_anchor : bool = False

class RAGContextRequest(BaseModel):
    query : str = Field(min_length=1)
    top_k : int = Field(default=5 , ge=1 , le=20)


class RAGContextResponse(BaseModel):
    query : str
    context : str

class RAGPrompt(BaseModel):
    system_prompt : str
    user_prompt : str


class RAGPromptResponse(BaseModel):
    query : str
    system_prompt : str
    user_prompt : str


class RAGSource(BaseModel):
    note_id : int
    chunk_id: int
    chunk_index: int
    content: str
    distance: float



class RAGAnswerResponse(BaseModel):
    query : str
    answer : str
    sources : list[RAGSource]


class RAGResult(BaseModel):
    answer : str
    sources : list[RetrievedChunk]














