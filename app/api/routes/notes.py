from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.note import (
    NoteCreate,
    NoteResponse,
    NoteUpdate,
    NoteListResponse,
    SemanticSearchResponse,
    NotePatch
)

from app.services.semantic_search_service import SemanticSearchService
from app.models.user import User
from app.services.note_service import NoteService
from app.core.security import get_current_user
from app.core.exceptions import InvalidNoteUpdateError

router = APIRouter(prefix="/notes" , tags=["Notes"])

@router.post("/", response_model=NoteResponse)
def create_note(
    note_data: NoteCreate,
    current_user : User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)

    return service.create_note(
        title=note_data.title,
        content=note_data.content,
        user_id=current_user.id
    )

@router.get("/search" , response_model=NoteListResponse)
def search_notes(query : str = Query(... , min_length=1), current_user : User = Depends(get_current_user), skip : int = Query(0 , ge = 0) , limit : int = Query(20 , ge = 1 ,le = 100),db : Session = Depends(get_db)):

    query = query.strip()
    if not query:
        raise ValueError("Query should not be empty")
    
    service = NoteService(db)
    return service.search_notes(user_id=current_user.id , query=query , skip=skip,limit=limit)

@router.get("/semantic-search" , response_model=SemanticSearchResponse)
def semantic_search(q : str = Query(... , min_length=1) , limit : int = Query(5 , ge=1 , le=20),db : Session = Depends(get_db) , current_user : User = Depends(get_current_user)):
    service = SemanticSearchService(db)

    results = service.search(user_id=current_user.id , query=q , limit=limit)

    items = [
        {
              "note_id": chunk.note_id,
            "chunk_id": chunk.id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "distance": float(distance)
        }
        for chunk , distance in results
    ]


    return {
        "items" : items ,
        "query" : q,
        "limit" : limit
    }

                    


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    current_user : User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)

    return service.get_note(note_id , current_user.id)

@router.get("/", response_model=NoteListResponse)
def get_notes(
    current_user : User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = NoteService(db)
    return service.get_notes(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user : User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)

    return service.update_note(
        note_id=note_id,
        title=note_data.title,
        content=note_data.content,
        user_id=current_user.id
    )

@router.patch("/{note_id}" , response_model=NoteResponse)
def patch_note(note_id : int , note_data : NotePatch , current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):

    service = NoteService(db=db)

    updates = note_data.model_dump(exclude_unset=True)

    if not updates:
      raise InvalidNoteUpdateError("Atleast one Field should be provided")

    return service.update_note(note_id=note_id , user_id=current_user.id , **updates)

@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    current_user : User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)

    service.delete_note(note_id,current_user.id)

    return {
        "message": "Note deleted successfully"
    }

