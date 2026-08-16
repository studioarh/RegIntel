import pytest


@pytest.mark.integration
def test_ingest_fixed_html_persists_document_chunks_and_vectors(
    db_session,
    fake_embed_documents,
) -> None:
    result = ingest_document(
        db=db_session,
        source_url="https://www.fca.org.uk/test-fixture",
        html_path="tests/fixtures/fca_example.html",
    )

    document = result.document

    assert document.id is not None
    assert document.content_hash is not None

    chunks = list(document.chunks)

    assert len(chunks) > 0
    assert all(chunk.text for chunk in chunks)
    assert all(chunk.embedding is not None for chunk in chunks)
    assert all(
        len(chunk.embedding) == 1024
        for chunk in chunks
    )