from apps.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    ForeignKey, 
    Enum,
    Text
    )
import enum
import json

class WorkflowType(str, enum.Enum):
    REG_DOC_ANALYSIS = "regulatory_document_analysis"


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

    state_json: Mapped[json] = mapped_column(
        JSONB,
        nullable=False
    )

    output_json: Mapped[json] = mapped_column(
        JSONB,
        nullable=False
    )

    outcome: Mapped[enum.Enum] = mapped_column(
        Enum(WorkflowOutcome, name="workflow_outcome"),
        nullable=False
    )



class ReviewTasks(Base):
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_runs.id"),
        nullable=False
    )

    document_id: Mapped[UUID] = mapped_column(
            ForeignKey("documents.id"),
            nullable=False
        )


