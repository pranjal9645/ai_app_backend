from sqlalchemy.orm import Session
from app.models.note import Note

class NoteRepository:

    def __init__(self , db : Session):
         self.db = db

    def create(self , note : Note):
         self.db.add(note)
         self.db.commit()
         self.db.refresh(note)

         return note

    def get_by_id(self , note_id : int):
         return (
              self.db.query(Note)
              .filter(Note.id == note_id)
              .first()
         )
    
    def get_all_by_user(self , user_id : int , skip : int = 0 , limit : int = 20):
         return (
              self.db.query(Note)
                  .filter(Note.user_id == user_id)
                  .order_by(Note.id)
                  .offset(skip)
                  .limit(limit)
                  .all()
         )

    def update(self , note : Note):
         self.db.commit()
         self.db.refresh(note)
         return note

    def delete(self , note : Note):
         self.db.delete(note)
         self.db.commit()


    def search_by_user(self , user_id : int , query : str , skip : int = 0 , limit : int = 20):
         search_pattern = f"%{query}%"

         return(
              self.db.query(Note)
                     .filter(Note.user_id == user_id , (
                          Note.title.ilike(search_pattern) | Note.content.ilike(search_pattern)
                     ))
                     .order_by(Note.id)
                     .offset(skip)
                     .limit(limit)
                     .all()
         )

    
        