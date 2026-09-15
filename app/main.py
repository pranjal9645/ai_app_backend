from fastapi import FastAPI , Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db

app = FastAPI(title = settings.app_name , version = settings.app_version)

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
