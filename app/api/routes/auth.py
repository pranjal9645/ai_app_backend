from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    TokenResponse , RefreshTokenRequest , ForgotPasswordRequest , ForgotPasswordResponse , ResetPasswordRequest , ResetPasswordResponse
)
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
from app.services.password_reset_service import PasswordResetService

router = APIRouter(prefix="/auth" , tags=["Authentication"])

@router.post("/login" , response_model=TokenResponse)
def login(form_data : OAuth2PasswordRequestForm = Depends() , db : Session = Depends(get_db)):
    service = AuthService(db)

    return service.login(email=form_data.username , password=form_data.password)

@router.post("/refresh" , response_model=TokenResponse)
def refresh(request : RefreshTokenRequest , db : Session = Depends(get_db)):
    service = AuthService(db=db)

    return service.refresh(refresh_token=request.refresh_token)

@router.post("/logout")
def logout(request : RefreshTokenRequest, db : Session = Depends(get_db)):
    service = AuthService(db=db)

    service.logout(refresh_token=request.refresh_token)

    return {
        "message" : "Logged out successfully"
    }

@router.post("/forgot-password" , response_model=ForgotPasswordResponse)
def forgot_password(request : ForgotPasswordRequest , db : Session = Depends(get_db)):

    service = PasswordResetService(db=db)

    message = service.request_password_reset(email=request.email)

    return {
          "message": message
    }


@router.post("/reset-password" , response_model=ResetPasswordResponse)
def reset_password(request : ResetPasswordRequest , db : Session = Depends(get_db)):

    service = PasswordResetService(db)

    service.reset_password(token=request.token , new_password=request.new_password)

    return {
         "message": "Password reset successfully."
    }