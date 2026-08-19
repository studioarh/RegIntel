from typing import Literal, TypedDict
from uuid import UUID

from src.agents.schema import ChangeExtraction, DocumentDiff ,EvidenceCitation, QualityDecision, RegulatoryBriefing


class WorkflowState(TypedDict, total=False):
    workflow_run_id: UUID
    trace_id: UUID
    document_id: UUID

    status: Literal["running", "approved", "review_required", "failed"]
    error_message: str | None

    document_title: str
    document_source_url: str
    document_published_at: str | None
    document_text: str

    diff: DocumentDiff
    evidence: list[EvidenceCitation]
    extraction: ChangeExtraction
    briefing: RegulatoryBriefing
    quality_decision: QualityDecision

    retrieval_config_version: str
    prompt_version: str
    model_config_version: str