from datetime import datetime , timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.base import Base

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id : Mapped[int] = mapped_column(primary_key=True)

    conversation_id : Mapped[int] = mapped_column(ForeignKey("conversations.id" , ondelete="CASCADE") , nullable=False , index=True)

    role : Mapped[str] = mapped_column(String(20) , nullable=False)

    content : Mapped[str] = mapped_column(Text , nullable=False)

    embedding : Mapped[list[float]] = mapped_column(Vector(768) , nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime , default=datetime.now(timezone.utc) , nullable=False)