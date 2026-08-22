import enum
import uuid
from enum import StrEnum
from typing import Any

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.db.session import Base


class WorkflowType(StrEnum):
    REG_DOC_ANALYSIS = "regulatory_document_analysis"


class ReviewReasonCode(StrEnum):
   
    NO_PRIOR_VERSION = "no_prior_version_found"
    DIFF_TRUNCATED = "diff_input_truncated"

    
    LOW_RETRIEVAL_SCORE = "retrieval_score_below_threshold"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"

    
    SCHEMA_VALIDATION_FAILED = "schema_validation_failed"
    CRITICAL_UNCERTAINTY = "critical_uncertainty_flag"

    
    CITATION_COVERAGE_LOW = "citation_coverage_below_threshold"
    UNRETRIEVED_CITATION = "unretrieved_citation_referenced"

class WorkflowOutcome(str, enum.Enum):
    APPROVED = "approved"
    REVIEW_REQUIRED = "review_required"
    FAILED = "failed"
    CRASHED = "crashed"



class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False
    )

    trace_id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True),
            nullable=False,
            default=uuid.uuid4
    )

    workflow_type: Mapped[WorkflowType] = mapped_column(
        Enum(WorkflowType, name="workflow_type"),
        nullable=False,
        default=WorkflowType.REG_DOC_ANALYSIS
    )

    retrieval_config_version: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    prompt_version: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    state_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )

    output_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )

    outcome: Mapped[WorkflowOutcome] = mapped_column(
        Enum(WorkflowOutcome, name="workflow_outcome"),
        nullable=False
    )



class ReviewTasks(Base):

    __tablename__ = "review_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ) 


    workflow_run_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_runs.id"),
        nullable=False
    )

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False
    )

    reason_codes: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        default=list
    )


