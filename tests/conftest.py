import pytest


from apps.db.models import Document, DocumentChunk


@pytest.fixture
def fake_embed_documents(monkeypatch):
    def fake_embed_documents(texts: list[str]) -> list[list[float]]:
        return [
            [float(index)]*1024 for index, _ in enumerate(texts, start=1)
        ]

    monkeypatch.setattr(
       
        "apps.api.app.services.chunking.embed_documents",
        fake_embed_documents,
    )

    return fake_embed_documents




@pytest.fixture
def motor_finance_chunk(db_session):
    document = Document(
        canonical_url="https://www.fca.org.uk/test-motor-finance",
        title="Motor finance fixture",
        content_hash="motor-finance-fixture-hash",
    )

    chunk = DocumentChunk(
        document=document,
        text="Over 800 promotions about motor finance claims were amended or withdrawn.",
        embedding=[1.0, 0.0, 0.0] + [0.0] * 1021,
    )

    db_session.add(chunk)
    db_session.commit()

    return chunk
    