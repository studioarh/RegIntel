from uuid import uuid4

from apps.api.app.services.validation import validate_answer_citations
from apps.schemas.answers import AnswerResponse, AnswerStatus, Citation


def test_valid_citation_is_accepted() -> None:
    chunk_id = uuid4()

    retrieved_chunks = [
        {
            "chunk_id": chunk_id,
            "text": "Over 800 promotions about motor finance claims were amended/withdrawn."
            
        }
    ]


    answer = AnswerResponse(
        status=AnswerStatus.ANSWERED,
        answer="Over 800 promotions about motor finance claims were amended or withdrawn.",
        citations=[
            Citation(
                chunk_id=chunk_id,
                document_title="FCA example",
                source_url="https://www.fca.org.uk/example",
                published_at=None,
                excerpt="Over 800 promotions about motor finance claims were amended/withdrawn."
            )
        ],
        confidence="medium",
        reason=None,
        trace_id=uuid4(),
    )

    valid, reason = validate_answer_citations(
        answer=answer,
        retrieved_chunks=retrieved_chunks,
    )

    assert valid is True
    assert reason is None


def test_non_retrieved_citation_is_rejected() -> None:
    retrieved_chunk_id = uuid4()
    invented_chunk_id = uuid4()

    retrieved_chunks = [
        {
            "chunk_id": retrieved_chunk_id,
            "text": "Evidence passage from the retrieved chunk.",
        }
    ]

    answer = AnswerResponse(
        status=AnswerStatus.ANSWERED,
        answer="An answer.",
        citations=[
            Citation(
                chunk_id=invented_chunk_id,
                document_title="Invented source",
                source_url="https://www.fca.org.uk/example",
                published_at=None,
                excerpt="Evidence passage from the retrieved chunk.",
            )
        ],
        confidence="medium",
        reason=None,
        trace_id=uuid4(),
    )

    valid, reason = validate_answer_citations(
        answer=answer,
        retrieved_chunks=retrieved_chunks,
    )

    assert valid is False
    assert "which was not part of the retrieval set." in reason



def test_verbatim_excerpt_is_accepted() -> None:
    chunk_id = uuid4()

    retrieved_chunks = [
        {
            "chunk_id": chunk_id,
            "text": "Over 800 promotions about motor finance claims were amended/withdrawn."
        }
    ]

    answer = AnswerResponse(
        status=AnswerStatus.ANSWERED,
        answer="Over 800 promotions were changed.",
        citations=[
            Citation(
                chunk_id=chunk_id,
                document_title="FCA example",
                source_url="https://www.fca.org.uk/example",
                published_at=None,
                excerpt="Over 800 promotions about motor finance claims were amended or withdrawn.",
            )
        ],
        confidence="medium",
        reason=None,
        trace_id=uuid4(),
    )

    valid, reason = validate_answer_citations(
        answer=answer,
        retrieved_chunks=retrieved_chunks,
    )

    

    assert valid is True
    assert reason is None

def test_answered_response_without_citations_is_rejected() -> None:
    answer = AnswerResponse(
        status=AnswerStatus.ANSWERED,
        answer="A supposedly supported answer.",
        citations=[],
        confidence="medium",
        reason=None,
        trace_id=uuid4(),
    )

    valid, reason = validate_answer_citations(
        answer=answer,
        retrieved_chunks=[],
    )

    assert valid is False
    assert "must contain at least one citation" in reason