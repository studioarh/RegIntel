import pytest



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
    