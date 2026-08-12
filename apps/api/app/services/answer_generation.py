from apps.api.app.services.retrieval import retrieve_chunks

from sqlalchemy.orm import Session
from datetime import date
from config.config import settings
from apps.db.models import QueryCitation, QueryRun
from pydantic import ValidationError
from apps.schemas.answers import AnswerResponse, AnswerStatus
from uuid import uuid4
from apps.api.app.services.llm import generate_answer_with_contract
from apps.api.app.services.validation import validate_retrieval_quality, validate_answer_citations




def generate_answer(
    db: Session,
    question: str,
    published_after: date | None = None,
    published_before: date | None = None,
) -> AnswerResponse:

    trace_id = uuid4()

    answer_candidates = retrieve_chunks(
     db=db,
     question=question,
     published_before=published_before,
     published_after=published_after
     )

    retrieval_ok, retrieval_reason = validate_retrieval_quality(answer_candidates)

    if not retrieval_ok:
        query_run = QueryRun(
                question=question,
                status=AnswerStatus.INSUFFICIENT_EVIDENCE,
                answer=None
                )
        db.add(query_run)
        db.commit()

        return AnswerResponse(
            status=AnswerStatus.INSUFFICIENT_EVIDENCE,
            answer=None,
            citations=[],
            confidence="low",
            reason=retrieval_reason,
            trace_id=trace_id,
        )

    context_chunks = answer_candidates[:settings.answer_context_count]

    raw_llm_output = generate_answer_with_contract(
        question=question,
        context_chunks=context_chunks,
        trace_id=trace_id
    )

    try:
        answer = AnswerResponse.model_validate_json(raw_llm_output)

    except ValidationError as exc:
        query_run = QueryRun(
                        question=question,
                        status=AnswerStatus.INSUFFICIENT_EVIDENCE,
                        answer=None
                    )
        db.add(query_run)
        db.commit()
        
        return AnswerResponse(
            status=AnswerStatus.INSUFFICIENT_EVIDENCE,
            answer=None,
            citations=[],
            confidence="low",
            reason="Model returned invalid answer schema.",
            trace_id=trace_id,
        )

    citations_ok, citations_reason = validate_answer_citations(
        answer=answer,
        retrieved_chunks=context_chunks
    )

    if not citations_ok:
        query_run = QueryRun(
                        question=question,
                        status=AnswerStatus.INSUFFICIENT_EVIDENCE,
                        answer=None
                    )
        db.add(query_run)
        db.commit()
        
        return AnswerResponse(
            status=AnswerStatus.INSUFFICIENT_EVIDENCE,
            answer=None,
            citations=[],
            confidence="low",
            reason=citations_reason,
            trace_id=trace_id,
        )

    validated_answer = AnswerResponse(
        **answer.model_dump(),
        confidence="medium",
        trace_id=trace_id,
    )

    query_run = QueryRun(
        question=question,
        status=validated_answer.status.value,
        answer=validated_answer.answer
        )
    
    db.add(query_run)
    db.flush()

    for position, citation in enumerate(
        validated_answer.citations, start=1
        ):
        db.add(
            QueryCitation(
                query_run_id=query_run.id,
                chunk_id=citation.chunk_id,
                excerpt=citation.excerpt,
                citation_order=position
            )
        )

    db.commit()

    return validated_answer


    

