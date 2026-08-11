from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session
from apps.api.app.services.ingestion import get_db
from apps.api.app.services.answer_generation import generate_answer



class AnswerRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2_000,
    )
    
    published_after: date | None = None
    published_before: date | None = None






router = APIRouter()
@router.post("/answer", response_model=AnswerResponse)
def answer_question(
    payload: AnswerRequest, 
    db: Session = Depends(get_db)
):
    result = generate_answer(
        db=db,
        question=payload.question,
        published_after=payload.published_after,
        published_before=payload.published_before,
    )

    return AnswerResponse(
        answer=result
    )