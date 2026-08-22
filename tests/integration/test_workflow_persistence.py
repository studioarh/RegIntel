from uuid import uuid4
from src.database.models.workflow import (
    WorkflowRun, 
    WorkflowType, 
    WorkflowOutcome, 
    ReviewTasks,
    ReviewReasonCode
    )
from sqlalchemy import select


def test_workflow_run_and_review_task_persistence(db_session, sample_document):

    run_id = uuid4()
    trace_id = uuid4()

    run = WorkflowRun(
        id=run_id,
        document_id=sample_document.id,
        trace_id=trace_id,
        workflow_type=WorkflowType.REG_DOC_ANALYSIS,
        retrieval_config_version="v1.0",
        prompt_version="v1.0",
        state_json={"step": "extraction_complete", "data": [1, 2, 3]},
        output_json={"briefing": "Test briefing summary"},
        outcome=WorkflowOutcome.REVIEW_REQUIRED
        )

    db_session.add(run)
    db_session.commit()

    saved_run = db_session.scalar(
        select(WorkflowRun).where(WorkflowRun.id == run_id)
        )
    assert saved_run is not None
    assert saved_run.outcome == WorkflowOutcome.REVIEW_REQUIRED
    assert saved_run.state_json["step"] == "extraction_complete"
    assert saved_run.trace_id == trace_id


    task_id = uuid4()
    task = ReviewTasks(
        id=task_id,
        workflow_run_id=saved_run.id,
        document_id=sample_document.id,
        reason_codes=[
            ReviewReasonCode.SCHEMA_VALIDATION_FAILED,
            ReviewReasonCode.CITATION_COVERAGE_LOW,
        ],
    )
    db_session.add(task)
    db_session.commit()

    
    saved_task = db_session.scalar(
        select(ReviewTasks).where(ReviewTasks.id == task_id)
        )
    assert saved_task is not None
    assert len(saved_task.reason_codes) == 2
    assert ReviewReasonCode.SCHEMA_VALIDATION_FAILED in saved_task.reason_codes
    
