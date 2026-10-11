from fastapi import FastAPI , Depends 
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.api.routes.users import router as users_router
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.routes.notes import router as notes_router
from app.core.exceptions import (
    UserAlreadyExistsError , UserNotFoundError , NoteNotFoundError , AuthenticationError , ConversationNotFoundError , MessageNotFoundError , AppException , AIServiceUnavailableError , RateLimitExceededError , RateLimitServiceUnavailableError
)
from app.api.routes.auth import router as auth_router
from app.api.routes.rag import router as rag_router
from app.api.routes.conversations import router as conversation_router
from app.api.routes.assistant import router as assistant_router

app = FastAPI(title = settings.app_name , version = settings.app_version)

app.include_router(users_router)
app.include_router(notes_router)
app.include_router(auth_router)
app.include_router(rag_router)
app.include_router(conversation_router)
app.include_router(assistant_router)

@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running",
        "environment": settings.environment
    }

@app.get("/health/database")
def database_health(db : Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "database": "connected"
    }

@app.exception_handler(AppException)
async def app_exception_handler(request : Request , exc : AppException):
    status_code = 400
    headers = {}

    if isinstance(exc , (UserNotFoundError , ConversationNotFoundError , MessageNotFoundError , NoteNotFoundError)):
        status_code = 404
    elif  isinstance(exc , UserAlreadyExistsError):
        status_code = 409
    elif isinstance(exc , AuthenticationError):
        status_code = 401
    elif isinstance(exc , AIServiceUnavailableError , RateLimitServiceUnavailableError):
        status_code = 503
    elif isinstance(exc , RateLimitExceededError):
        status_code = 429
        headers["Retry-After"] = str(exc.retry_after)

    return JSONResponse(
        status_code=status_code , 
        content={
            "error" :{
                "code" : exc.code,
                "message" : str(exc)
            }
        },
        headers=headers
    )
