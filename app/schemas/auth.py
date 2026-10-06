from pydantic import BaseModel , EmailStr
from app.schemas.user import UserResponse

class TokenResponse(BaseModel):
    access_token : str
    refresh_token : str
    token_type : str

class RefreshTokenRequest(BaseModel):
    refresh_token : str

class RegisterResponse(BaseModel):
    user : UserResponse
    access_token : str
    refresh_token : str
    token_type : str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    message: str
