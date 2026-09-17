from sqlalchemy.orm import Session
from app.models.note import Note
from app.repositories.note_repository import NoteRepository
from app.core.exceptions import NoteNotFoundError

class NoteService:

    def __init__(self , db : Session):
        self.note_repository = NoteRepository(db)

    def create_note(self , title : str , content : str , user_id : int):
        note = Note(title = title , content = content , user_id = user_id)

        return self.note_repository.create(note)

    def get_note(self , note_id : int , user_id : int):
        note = self.note_repository.get_by_id(note_id)

        if not note:
            raise NoteNotFoundError("Note not found")

        if note.user_id != user_id:
            raise NoteNotFoundError("Note not found")

        return note

    def get_notes(self , user_id : int , skip : int = 0 , limit : int = 20):
        return (
            self.note_repository.get_all_by_user(user_id=user_id , skip=skip,limit=limit)
        )

    def update_note(self , note_id : int , title : str , content : str , user_id : int):

        note = self.note_repository.get_by_id(note_id)
        if not note:
            raise NoteNotFoundError("Note not found")

        if note.user_id != user_id:
            raise NoteNotFoundError("Note not found")

        note.title = title
        note.content = content

        return self.note_repository.update(note)

    def delete_note(self, note_id: int , user_id : int):

      note = self.note_repository.get_by_id(note_id)

      if not note:
        raise NoteNotFoundError("Note not found")

      if note.user_id != user_id:
           raise NoteNotFoundError("Note not found")

      self.note_repository.delete(note)

    

    