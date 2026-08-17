import pytest
from apps.db.models import (
    Document,
    DocumentChunk,
    IngestionRun,
)

@pytest.mark.integration
def test_ingest_fixed_html_persists_document_chunks_and_vectors(
    db_session,
    client,
    fake_embed_documents,
) -> None:

    response = client.post(
        "/v1/documents/ingest",
        json={
            "source_url": (
                "https://www.fca.org.uk/publications/consultation-papers/cp26-15-reviewing-financial-promotions-rules-consumer-credit"
            ),
        },
    )

    assert response.status_code in (200, 201, 202)

    payload = response.json()

    run = db_session.get(
        IngestionRun,
        payload["ingestion_run_id"],
    )

    assert run is not None
    assert run.document_id is not None

    document = db_session.get(
        Document,
        run.document_id,
    )

    assert document is not None

    chunks = (
        db_session.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .all()
    )

    assert chunks
    assert all(chunk.text for chunk in chunks)
    assert all(chunk.embedding is not None for chunk in chunks)
    assert all(
        len(chunk.embedding) == 1024
        for chunk in chunks
    )