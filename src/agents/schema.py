from pydantic import BaseModel, AnyHttpUrl, Field
from datetime import date
from uuid import UUID
from typing import Literal



class EvidenceCitation(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_title: str
    source_url: AnyHttpUrl
    excerpt: str = Field(min_length=1)
    relevance_score: float
    published_at: date | None = None

     
        

class RegulatoryFact(BaseModel):
    fact_type: Literal[
        "obligation", "deadline", "scope", "effective_date",
        "enforcement", "consultation", "other"
    ]
    statement: str
    sector: Literal["consumer_lending", "unknown"]
    citation_chunk_ids: list[UUID] = Field(min_length=1)
    uncertainty: str | None = None

class QualityDecision(BaseModel):
    status: Literal["approved", "review_required"]
    reasons: list[str]
    citation_coverage: float
    extraction_valid: bool
    retrieval_score: float | None = None

class ModifiedPassage(BaseModel):
    before: str = Field(min_length=1)
    after: str = Field(min_length=1)


class DocumentDiff(BaseModel):
    previous_document_id: UUID | None = None
    change_detected: bool
    added_passages: list[str]
    removed_passages: list[str]
    modified_passages: list[ModifiedPassage] = Field(default_factory=list)
    was_truncated: bool = False


class ChangeExtraction(BaseModel):
    regulator: str = Field(min_length=1)
    document_type: str
    summary: str
    affected_sectors: list[str] = Field(default_factory=list)
    facts: list[RegulatoryFact] = Field(default_factory=list)
    uncertainty_flags: list[str] = Field(default_factory=list)
    publication_date: date | None = None
    


class BriefingClaim(BaseModel):
    statement: str
    citation_chunk_ids: list[UUID]
    claim_kind: Literal["source_fact", "analyst_interpretation"]


class RegulatoryBriefing(BaseModel):
    document_id: UUID
    title: str
    source_url: AnyHttpUrl
    what_changed: list[BriefingClaim] = Field(default_factory=list)
    why_it_may_matter: list[BriefingClaim] = Field(default_factory=list)
    key_dates: list[BriefingClaim] = Field(default_factory=list)
    uncertainty_flags: list[str] = Field(default_factory=list)
    publication_date: date | None = None
    
   