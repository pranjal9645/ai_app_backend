from sqlalchemy.orm import Session
from app.models.note_chunk import NoteChunk
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.repositories.note_repository import NoteRepository


class EmbeddingIngestionService:

    def __init__(self , db : Session):
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.note_repository = NoteRepository(db)

    def process_note(self , note_id : int , content : str) -> list[NoteChunk]:

        chunks = self.chunking_service.chunk_text(content)

        if not chunks:
            raise ValueError(
                "Note content produced no chunks"
            )

        note_chunks = []

        for index , chunk_text in enumerate(chunks):
            embedding = self.embedding_service.create_embedding(chunk_text)

            note_chunk = NoteChunk(note_id = note_id , content = chunk_text , chunk_index = index , embedding = embedding)

            note_chunks.append(note_chunk)


        return self.note_repository.create_chunks(chunks=note_chunks)

    def rebuild_note(self  , note_id : int , content : str ) -> list[NoteChunk]:

        self.note_repository.delete_chunks_by_note_id(note_id=note_id)

        return self.process_note(note_id=note_id ,content=content)
    

