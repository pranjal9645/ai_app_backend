from fastapi import FastAPI , Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.api.routes.users import router as users_router
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    UserAlreadyExistsError , UserNotFoundError
)

app = FastAPI(title = settings.app_name , version = settings.app_version)

app.include_router(users_router)

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

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request : Request , exc : UserNotFoundError):
    return JSONResponse(status_code=404 
                        , content= {
                            "detail" : str(exc)
                        }
                    )
@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(request : Request , exc : UserAlreadyExistsError):
    return JSONResponse(status_code=409 , content={
        "detail" : str(exc)
    }
 )