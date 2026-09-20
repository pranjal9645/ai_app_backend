from app.repositories.note_repository import NoteRepository
from app.services.embedding_service import EmbeddingService
from sqlalchemy.orm import Session

class SemanticSearchService:

    def __init__(self , db : Session):
        self.embedding_service = EmbeddingService()
        self.note_repository = NoteRepository(db)

    def search(self  , user_id : int , query : str , limit : int = 5):
        query_embedding = self.embedding_service.create_embedding(query)

        return self.note_repository.semantic_search(user_id=user_id , query_embedding=query_embedding , limit=limit)