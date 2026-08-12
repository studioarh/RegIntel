from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, AnyHttpUrl


class Citation(BaseModel):
    chunk_id: UUID
    document_title: str
    source_url: AnyHttpUrl
    published_at: date | None
    excerpt: str = Field(min_length=1)


class AnswerStatus(str, Enum):
    ANSWERED = "answered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class AnswerResponse(BaseModel):
    status: AnswerStatus
    answer: str | None
    citations: list[Citation]
    confidence: Literal["low", "medium", "high"]
    reason: str | None = None
    trace_id: UUID






