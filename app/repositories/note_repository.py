from sqlalchemy.orm import Session
from app.models.note import Note
from sqlalchemy import func , select
from app.models.note_chunk import NoteChunk
from sqlalchemy import delete
import math


class NoteRepository:

    def __init__(self , db : Session):
         self.db = db

    def create(self , note : Note):
         self.db.add(note)
         self.db.flush()
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
         self.db.flush()
         self.db.refresh(note)
         return note

    def delete(self , note : Note):
         self.db.delete(note)
         self.db.flush()


    def search_by_user(self , user_id : int , query : int , skip : int = 0 , limit : int = 20):
       search_vector = func.to_tsvector("english" , Note.title + " " + Note.content)
       search_query = func.plainto_tsquery("english" , query)

       return (
          self.db.query(Note)
                 .filter(
                      Note.user_id == user_id ,
                      search_vector.op("@@")(search_query)
                 )
                 .order_by(func.ts_rank(
                      search_vector,
                      search_query
                 ).desc() , Note.id)
                 .offset(skip)
                 .limit(limit)
                 .all()
     )
    
    def count_by_user(self , user_id : int):
         return (
              self.db.query(Note)
                     .filter(Note.user_id == user_id)
                     .count()
         )

    def count_search_by_user(self , user_id : int , query : str):
         search_vector = func.to_tsvector("english" , Note.title + " " + Note.content)

         search_query = func.plainto_tsquery("english" , query)
         
         return (
        self.db.query(Note)
        .filter(
            Note.user_id == user_id,
            search_vector.op("@@")(search_query)
        )
        .count()
    )

    def semantic_search(self  , user_id : int , query_embedding : list[float] ,limit : int = 5) -> list[tuple[NoteChunk , float]]:
         distance = NoteChunk.embedding.cosine_distance(query_embedding)

         statement = (
              select(NoteChunk , distance.label("distance"))
              .join(Note , Note.id == NoteChunk.note_id)
              .where(Note.user_id == user_id)
              .order_by(distance)
              .limit(limit)
         )

         return list(self.db.execute(statement).all())

    def get_neighbor_chunks(self , user_id : int , note_id : int , chunk_index : int , radius : int = 1) -> list[NoteChunk]:
         statement = (
              select(NoteChunk)
              .join(Note , Note.id == NoteChunk.note_id)
              .where(
                   Note.user_id == user_id,
                   NoteChunk.note_id == note_id,
                   NoteChunk.chunk_index >= chunk_index - radius,
                   NoteChunk.chunk_index <= chunk_index + radius
              )
              .order_by(NoteChunk.chunk_index)
         )

         return list(self.db.execute(statement).scalars().all())
    
    
    def create_chunks(self , chunks : list[NoteChunk]) -> list[NoteChunk]:
         self.db.add_all(chunks)
         self.db.flush()

         return chunks
     
    def delete_chunks_by_note_id(self , note_id : int) -> None:
         self.db.execute(
              delete(NoteChunk).where(
                   NoteChunk.note_id == note_id
              )
         )

         self.db.flush()

    def full_text_search(self , user_id : int , query : int , limit : int = 5) -> list[tuple[NoteChunk , float]]:
         search_vector = func.to_tsvector("english" , Note.content)
         search_query = func.plainto_tsquery("english" , query)

         rank = func.ts_rank(search_vector , search_query)

         statement = (
              select(NoteChunk , rank.label("rank"))
              .join(Note , Note.id == NoteChunk.note_id)
               .where(Note.user_id == user_id ,
                      search_vector.op("@@")(search_query)
                    )
               .order_by(rank.desc())
               .limit(limit)
         )

         return list(
              self.db.execute(statement).all()
         )

    def get_note_chunks(self , user_id : int) -> list[NoteChunk]:
         statement = (
              select(NoteChunk)
              .join(Note , Note.id == NoteChunk.note_id)
              .where(Note.user_id == user_id)
              .order_by(NoteChunk.note_id , NoteChunk.chunk_index)
         )

         return list(self.db.execute(statement).scalars().all())

    def semantic_search_with_raw_content_embedding(self , user_id : int , note_chunks : list[NoteChunk] , content_embeddings : list[list[float]] , query_embedding : list[float] , limit : int = 5) -> list[tuple[NoteChunk , float]]:
             results = []
    
             for chunk, content_embedding in zip(note_chunks, content_embeddings):
               distance = self.cosine_distance(
                 query_embedding,
                 content_embedding,
               )
    
               results.append((chunk, distance))
    
             results.sort(key=lambda item: item[1])
    
             return results[:limit]

    def cosine_distance(self, vector_a: list[float],vector_b: list[float],) -> float:

     dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )
 
     magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

     magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

     if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError("Cannot calculate cosine distance for a zero vector.")

     cosine_similarity = (
        dot_product / (magnitude_a * magnitude_b)
    )

     return 1.0 - cosine_similarity
          
    


        