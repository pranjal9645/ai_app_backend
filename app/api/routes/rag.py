from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.rag import (
    RAGContextRequest , RAGContextResponse , RAGPromptResponse , RAGAnswerResponse , RAGSource
)
from app.models.user import User

from app.services.rag_service import RagService
from app.core.security import get_current_user

router = APIRouter(prefix="/rag" , tags=["RAG"])

@router.post("/context" , response_model=RAGContextResponse)
def build_rag_context(request : RAGContextRequest , db : Session = Depends(get_db) , current_user : User = Depends(get_current_user)):
    service = RagService(db)

    context = service.build_context(user_id=current_user.id , query=request.query , top_k=request.top_k)

    return RAGContextResponse(query=request.query , context=context)

@router.post("/prompt" , response_model=RAGPromptResponse)
def build_rag_prompt(request : RAGContextRequest , db : Session = Depends(get_db) , current_user : User = Depends(get_current_user)):
    service = RagService(db)

    prompt = service.build_prompt(user_id=current_user.id , query=request.query , top_k=request.top_k)

    return RAGPromptResponse(
        query=request.query,
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt
    )
@router.post("/answer" , response_model=RAGAnswerResponse)
def generate_rag_answer(request : RAGContextRequest , db : Session = Depends(get_db) , current_user : User = Depends(get_current_user)):
    service = RagService(db)

    result = service.generate_answer(user_id=current_user.id , query=request.query , top_k=request.top_k)

    return RAGAnswerResponse(
        query=request.query,
        answer=result.answer,
        sources=[
            RAGSource(
                note_id=source.note_id,
                chunk_id=source.chunk_id,
                chunk_index=source.chunk_index,
                content=source.content,
                distance=source.distance,
                retrieval_sources=source.retrieval_sources,
                hybrid_score=source.hybrid_score
            )
           for source in result.sources
        ]
    )


     
