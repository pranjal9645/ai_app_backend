from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.note import (
    NoteCreate,
    NoteResponse,
    NoteUpdate,
)
from app.models.user import User
from app.services.note_service import NoteService
from app.core.security import get_current_user

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


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    current_user : User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)

    return service.get_note(note_id , current_user.id)

@router.get("/", response_model=list[NoteResponse])
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