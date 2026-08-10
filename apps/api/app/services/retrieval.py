from datetime import date

from apps.api.app.services.embedding import embed_question
from apps.db.models import Document, DocumentChunk
from sqlalchemy import select
from sqlalchemy.orm import Session


def retrieve_chunks(
        db: Session,
        question: str,
        published_before: date | None = None,
        published_after: date  | None = None

) -> list[dict]:
    query = embed_question(question)

    distance = DocumentChunk.embedding.cosine_distance(query)

    similarity = (1 - distance).label("similarity")

    statement = (
        select(
            DocumentChunk,
            Document,
            similarity
        ). join(
            Document,
            DocumentChunk.document_id == Document.id 
        ).where(DocumentChunk.embedding.is_not(None))
        . order_by(distance)
        .limit(10)

    )


    
    if published_before is not None:
        statement = statement.where(
            Document.published_at <= published_before
        )

    if published_after is not None:
            statement = statement.where(
                Document.published_at <= published_after
            )

    result_rows = db.execute(statement).all()

    return [
            {
                "chunk_id": str(chunk.id),
                "document_id": str(document.id),
                "text": chunk.text,
                "similarity": float(score),
    
                "section_heading": chunk.section_heading,
                "page_number": chunk.page_number,
    
                "url": document.canonical_url,
                "title": document.title,
                "published_at": document.published_at,
                "document_type": document.source_type,
            }
            for chunk, document, score in result_rows
    ]




