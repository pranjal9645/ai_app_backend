from sqlalchemy.orm import Session
from app.models.note import Note
from app.repositories.note_repository import NoteRepository
from app.core.exceptions import NoteNotFoundError
from app.services.redis_service import RedisService
from app.schemas.note import NoteListResponse
from app.services.embedding_ingestion_service import EmbeddingIngestionService


class NoteService:

    def __init__(self , db : Session):
        self.db = db
        self.note_repository = NoteRepository(db)
        self.redis_service = RedisService()
        self.embedding_ingestion_service = EmbeddingIngestionService(db)


    def invalidate_notes_cache(self , user_id : int):
        version_key = f"notes:user:{user_id}:version"
        self.redis_service.increment(version_key)

    def create_note(self , title : str , content : str , user_id : int):
        try:
          note = Note(title = title , content = content , user_id = user_id)
          note = self.note_repository.create(note)
       
          self.embedding_ingestion_service.process_note(note_id=note.id , content=note.content)
          self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        self.invalidate_notes_cache(user_id=user_id)
        return note


    def get_note(self , note_id : int , user_id : int):
        note = self.note_repository.get_by_id(note_id)

        if not note:
            raise NoteNotFoundError("Note not found")

        if note.user_id != user_id:
            raise NoteNotFoundError("Note not found")

        return note

    def get_notes(self , user_id : int , skip : int = 0 , limit : int = 20):
        
          version_key = f"notes:user:{user_id}:version"

          version = self.redis_service.get_int(version_key)

          if version is None:
              version = self.redis_service.increment(version_key)

          cache_key = f"notes:user:{user_id}:v:{version}:list:{skip}:{limit}"

          cached_notes = self.redis_service.get(cache_key)

          if cached_notes is not None:
              return cached_notes

          notes = self.note_repository.get_all_by_user(user_id=user_id,skip=skip,limit=limit)

          total = self.note_repository.count_by_user(user_id=user_id)

          result = NoteListResponse(
             items=notes,
             total=total,
             skip=skip,
             limit=limit,
             has_more=(skip + len(notes)) < total
         ).model_dump(mode="json")

          self.redis_service.set(cache_key , result , ex=60)

          return result

         
        

    def update_note(self , note_id : int , title : str , content : str , user_id : int):

        note = self.note_repository.get_by_id(note_id)
        if not note:
            raise NoteNotFoundError("Note not found")

        if note.user_id != user_id:
            raise NoteNotFoundError("Note not found")

        content_changed = note.content != content

        try:
          note.title = title
          note.content = content

          note = self.note_repository.update(note)
       

          if content_changed:
            self.embedding_ingestion_service.rebuild_note(note_id=note.id , content=note.content)

          self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.invalidate_notes_cache(user_id=user_id)

        return note

    def delete_note(self, note_id: int , user_id : int):

      note = self.note_repository.get_by_id(note_id)

      if not note:
        raise NoteNotFoundError("Note not found")

      if note.user_id != user_id:
           raise NoteNotFoundError("Note not found")
      try:
        self.note_repository.delete(note)
        self.db.commit()
      except Exception:
          self.db.rollback()
          raise

      self.invalidate_notes_cache(user_id=user_id)
      

    def search_notes(self , user_id : int , query : str , skip : int = 0 , limit : int = 20):
        notes =  self.note_repository.search_by_user(user_id=user_id , query=query,skip=skip,limit=limit)
        total = self.note_repository.count_search_by_user(user_id=user_id , query=query)

        return {
        "items": notes,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + len(notes)) < total
    }

    

    