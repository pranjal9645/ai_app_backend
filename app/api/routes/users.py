from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate
from app.services.user_service import UserService


router = APIRouter(prefix="/users" , tags=["Users"])

@router.post("/")
def create_user(user_data : UserCreate , db : Session = Depends(get_db)):
    service = UserService(db)

    return service.create_user(name=user_data.name , email=user_data.email)