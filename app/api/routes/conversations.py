from fastapi import APIRouter , Depends , status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.conversation import (
    ConversationChatResponse,
    ConversationCreateRequest,
    ConversationMessageRequest,
    ConversationMessageResponse,
    ConversationResponse,
)

from app.services.conversation_service import ConversationService
from app.core.security import get_current_user
from app.schemas.rag import RAGSource
from app.core.rate_limit import rate_limit , rate_limit_by_user

router = APIRouter(prefix="/conversations" , tags=["Conversations"])

@router.post("" , response_model=ConversationResponse)
def create_conversation(request : ConversationCreateRequest , current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):
    conversation_service = ConversationService(db = db)

    return conversation_service.create_conversation(user_id=current_user.id , title=request.title)


@router.get("" , response_model=list[ConversationResponse])
def get_conversations(current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):
    conversation_service = ConversationService(db=db)

    return conversation_service.get_conversations(user_id=current_user.id)


@router.get("/{conversation_id}" , response_model=ConversationResponse)
def get_conversation(conversation_id : int , current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):
    conversation_service = ConversationService(db=db)

    return conversation_service.get_conversation(conversation_id=conversation_id , user_id=current_user.id)

@router.get("/{conversation_id}/messages" , response_model=list[ConversationMessageResponse])
def get_messages(conversation_id : int , current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):
    conversation_service = ConversationService(db=db)

    messages = conversation_service.get_messages(user_id=current_user.id , conversation_id=conversation_id)

    return messages

@router.post("/{conversation_id}/messages" , response_model=ConversationChatResponse , dependencies=[Depends(rate_limit(30,60)) , Depends(rate_limit_by_user(10,60))])
def send_message(conversation_id : int , request : ConversationMessageRequest , current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):
    conversation_service = ConversationService(db=db)

    result = conversation_service.send_message(user_id=current_user.id , conversation_id=conversation_id , content=request.message).rag_result

    return ConversationChatResponse(
        conversation_id=conversation_id,
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

@router.delete("/{conversation_id}/messages/{message_id}")
def delete_message(conversation_id : int , message_id : int , current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):
    conversation_service = ConversationService(db=db)

    conversation_service.delete_message(user_id=current_user.id , conversation_id=conversation_id , message_id=message_id)

    return {
        "detail" : "Message deleted Successfully"
    }


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id : int , current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):
    conversation_service = ConversationService(db=db)

    conversation_service.delete_conversation(user_id=current_user.id , conversation_id=conversation_id)

    return {
        "detail" : "Conversation Deleted Successfully"
    }

                 