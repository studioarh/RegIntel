from config.config import settings
from apps.schemas.answers import AnswerResponse, AnswerStatus


def validate_retrieval_quality(
        candidates: list[dict]
) -> tuple[bool, str | None]:

    if not candidates:
        return False, "no retrieval candidates found"

    threshold = settings.similarity_threshold

    strong = [ c for c in candidates if c["similarity"] >= threshold ]

    if len(strong) < settings.min_credible_chunks:
        return (
            False,
            "Too few high-similarity chunks to support a reliable answer.",
        )

    return True, None


def validate_answer_citations(
        answer: AnswerResponse,
        retrieved_chunks: list[dict]
) -> tuple[bool, str | None]:
    if answer.status == AnswerStatus.ANSWERED:
        if not answer.citations:
            return (
                False,
                "Answered response must contain at least one citation.",
            )
    else:
        return True, None

    chunk_text_by_id = {
        c["chunk_id"]: c["text"] for c in retrieved_chunks
    }

    for citation in answer.citations:
        chunk_text = chunk_text_by_id.get(citation.chunk_id)
        if chunk_text is None:
            return (
                False,
                f"Citation references chunk_id {citation.chunk_id} which was not part of the retrieval set."
            )

        if citation.excerpt not in chunk_text:
            return (
                False,
                f"Citation excerpt for chunk {citation.chunk_id} is not a substring of the stored chunk text."
                
            )

    return True, None
    