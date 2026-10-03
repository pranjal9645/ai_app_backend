from fastapi import Depends , APIRouter
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.assistant import (AssistantChatRequest , AssistantChatResponse)
from app.services.assistant_service import AssistantService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/assistant" , tags=["Assistant"])

@router.post("/chat" , response_model=AssistantChatResponse)
def chat(request : AssistantChatRequest , db : Session = Depends(get_db) , current_user : User = Depends(get_current_user)):
    assistant_service = AssistantService(db=db)

    return assistant_service.chat(user_id=current_user.id , request=request)
