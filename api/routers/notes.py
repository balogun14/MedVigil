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

@router.get("/api/notes/{note_id}/naranjo-draft")
def get_naranjo_draft(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    # Mock auto-filling logic based on entities
    questions = [
        {"id": 1, "text": "Are there previous conclusive reports on this reaction?", "suggested_answer": 0},
        {"id": 2, "text": "Did the adverse event appear after the suspected drug was administered?", "suggested_answer": 2},
        {"id": 3, "text": "Did the adverse event improve when the drug was discontinued?", "suggested_answer": 1 if "discontinuing" in note.text.lower() else 0},
        {"id": 4, "text": "Did the adverse event reappear when the drug was readministered?", "suggested_answer": 0},
        {"id": 5, "text": "Are there alternative causes that could on their own have caused the reaction?", "suggested_answer": 0},
        {"id": 6, "text": "Did the reaction reappear when a placebo was given?", "suggested_answer": 0},
        {"id": 7, "text": "Was the drug detected in blood (or other fluids) in concentrations known to be toxic?", "suggested_answer": 0},
        {"id": 8, "text": "Was the reaction more severe when the dose was increased?", "suggested_answer": 0},
        {"id": 9, "text": "Did the patient have a similar reaction to the same or similar drugs in any previous exposure?", "suggested_answer": 0},
        {"id": 10, "text": "Was the adverse event confirmed by any objective evidence?", "suggested_answer": 0},
    ]
    return {"questions": questions}

class NaranjoSubmission(BaseModel):
    answers: List[int]

@router.post("/api/notes/{note_id}/naranjo")
def calculate_naranjo(note_id: int, submission: NaranjoSubmission, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    score = sum(submission.answers)
    
    if score >= 9:
        classification = "Definite"
    elif score >= 5:
        classification = "Probable"
    elif score >= 1:
        classification = "Possible"
    else:
        classification = "Doubtful"
        
    note.naranjo_score = score
    note.naranjo_classification = classification
    session.add(note)
    session.commit()
    session.refresh(note)
    
    return {"score": score, "classification": classification}
