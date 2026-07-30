from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel
from fastapi import Depends, Response, status
from sqlalchemy.orm import Session

from apps.api.app.main import app
from apps.db.models import IngestionRun
from apps.db.session import SessionLocal


class IngestRequest(BaseModel):
    url: AnyHttpUrl


class IngestionUrlResponse(BaseModel):
    ingestion_id: UUID | None = None
    status: str


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


def process_ingestion_run(db: Session, run_id: UUID ):


@app.post("/v1/documents/ingest", response_model=IngestionUrlResponse)
def create_ingestion_run(
    payload: IngestRequest, 
    response: Response,  
    db: Session = Depends(get_db)
    ):

    allowed_hosts={
        'fca.org.uk', 
        'register.fca.org.uk',
        'handbook.fca.org.uk',
        'www.fca.org.uk', 
        'www.register.fca.org.uk',
        'www.handbook.fca.org.uk'
        }

    if payload.url.host not in allowed_hosts:
        response.status_code=status.HTTP_400_BAD_REQUEST

        return IngestionUrlResponse(status="Rejected - Not an FCA Url")

    response.status_code=status.HTTP_202_ACCEPTED

    run = IngestionRun(source_url=payload.url)

    db.add(run)
    db.commit()
    db.refresh(run)

    process_ingestion_run(db, run.id)

    return run




@app.get("/v1/ingestion-runs/{run_id}")
def 