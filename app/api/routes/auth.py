from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    TokenResponse
)
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth" , tags=["Authentication"])

@router.post("/login" , response_model=TokenResponse)
def login(form_data :OAuth2PasswordRequestForm = Depends() , db : Session = Depends(get_db)):
    service = AuthService(db)

    access_token = service.login(email=form_data.username , password=form_data.password)

    return {
         "access_token": access_token,
         "token_type": "bearer"
    }