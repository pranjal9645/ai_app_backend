from fastapi import Depends , APIRouter
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.assistant import (AssistantChatRequest , AssistantChatResponse)
from app.services.assistant_service import AssistantService
from app.core.security import get_current_user
from app.models.user import User
from app.core.rate_limit import rate_limit , rate_limit_by_user

router = APIRouter(prefix="/assistant" , tags=["Assistant"] , dependencies=[Depends(rate_limit(30,60)) , Depends(rate_limit_by_user(10,60))])

@router.post("/chat" , response_model=AssistantChatResponse)
def chat(request : AssistantChatRequest , db : Session = Depends(get_db) , current_user : User = Depends(get_current_user)):
    assistant_service = AssistantService(db=db)

    return assistant_service.chat(user_id=current_user.id , request=request)
