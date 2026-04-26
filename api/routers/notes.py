from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel

from core.database import get_session
from models.note import Note
from brain.scripts.inference import MedVigilBrain
from brain.scripts.rag import RAGAgent

router = APIRouter()
brain = MedVigilBrain()
rag_agent = RAGAgent()

class NoteRequest(BaseModel):
    text: str

@router.post("/api/notes")
def submit_note(request: NoteRequest, session: Session = Depends(get_session)):
    analysis = brain.analyze_note(request.text)
    
    note = Note(
        text=analysis["clean_text"],
        entities=analysis["entities"]
    )
    
    session.add(note)
    session.commit()
    session.refresh(note)
    
    return {"id": note.id, "status": note.status}

@router.get("/api/notes/{note_id}")
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/api/notes/{note_id}/literature-search")
def search_literature(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    # Run the RAG literature search using extracted entities
    result = rag_agent.search_literature(note.entities)
    return result
