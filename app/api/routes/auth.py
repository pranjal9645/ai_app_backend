from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth" , tags=["Authentication"])

@router.post("/login" , response_model=TokenResponse)
def login(login_data : LoginRequest , db : Session = Depends(get_db)):
    service = AuthService(db)

    access_token = service.login(email=login_data.email , password=login_data.password)

    return {
         "access_token": access_token,
         "token_type": "bearer"
    }