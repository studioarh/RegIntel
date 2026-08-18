import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from apps.api.app.main import app
from apps.api.app.services.ingestion import get_db
from apps.db.models import Document, DocumentChunk
from apps.db.session import Base

TEST_DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/regintel_test"


test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def create_test_schema() -> None:
    with test_engine.begin() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)




@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def db_session() -> Session:
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()

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
        
        source_type="html",
        
        raw_storage_path="test.pdf",
        
        published_at="2026-08-17",
        cleaned_text="test",
        sector=None,
    )

    chunk = DocumentChunk(
        document=document,
        text="Over 800 promotions about motor finance claims were amended or withdrawn.",
        embedding=[1.0, 0.0, 0.0] + [0.0] * 1021,

        document_id=document.id,
        page_number=2,
        chunk_index=1,
                        
        section_heading="test",
        char_start=1,
        char_end=2,
                        
    )

    db_session.add(chunk)
    db_session.commit()

    return chunk

    