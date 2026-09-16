from datetime import datetime
from sqlalchemy import DateTime , ForeignKey , String , Text
from sqlalchemy.orm import Mapped , mapped_column
from app.db.base import Base

class Note(Base):
    __tablename__ = "notes"

    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(String(255) , nullable=False)
    content : Mapped[str] = mapped_column(Text , nullable=False)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow , nullable=False)
    updated_at : Mapped[datetime] = mapped_column(DateTime , default=datetime.utcnow , onupdate=datetime.utcnow,nullable=False)
