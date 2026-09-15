
from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy.orm import sessionmaker
from collections.abc import Generator
from sqlalchemy.orm import Session


engine = create_engine(settings.database_url , echo=True)

SessionLocal = sessionmaker(bind=engine , autoflush=False, autocommit=False)

def get_db() -> Generator[Session , None , None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

