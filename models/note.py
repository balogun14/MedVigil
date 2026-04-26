from sqlmodel import SQLModel, Field, JSON
from typing import Optional, List, Dict, Any

class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    entities: List[Dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    status: str = Field(default="processed")
    naranjo_score: Optional[int] = Field(default=None)
    naranjo_classification: Optional[str] = Field(default=None)
