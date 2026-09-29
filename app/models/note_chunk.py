from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime , ForeignKey , Text
from sqlalchemy.orm import Mapped , mapped_column
from app.db.base import Base

class NoteChunk(Base):

    __tablename__ = "note_chunks"

    id : Mapped[int] = mapped_column(primary_key=True)
    note_id : Mapped[int] = mapped_column(ForeignKey("notes.id" , ondelete="CASCADE"), nullable=False , index=True)
    content : Mapped[str] = mapped_column(Text , nullable=False)
    contextual_content : Mapped[str] = mapped_column(Text , nullable=False)
    chunk_index : Mapped[int] = mapped_column(nullable=False)
    embedding : Mapped[list[float]] = mapped_column(Vector(768) , nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime , default=datetime.utcnow , nullable=False)
