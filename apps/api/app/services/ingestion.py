from datetime import datetime, timezone
from uuid import UUID

import httpx
from apps.api.app.services.extraction import (
    ExtractionError,
    content_hash,
    download_document,
    extract_document,
)

from apps.api.app.services.storage import save_raw_content
from apps.db.models import Document, IngestionRun, IngestionStatus, DocumentChunk
from apps.db.session import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import AnyHttpUrl, BaseModel
from sqlalchemy.orm import Session
from chunking import draft_chunk_records



router = APIRouter()
class IngestRequest(BaseModel):
    url: AnyHttpUrl


class IngestionUrlResponse(BaseModel):
     ingestion_id: UUID | None = None
     document_url: str | None = None
     status: str
     created_at: datetime  | None = None
     started_at: datetime | None = None
     completed_at: datetime | None = None
    

class IngestionRunResponse(BaseModel):
    ingestion_id: UUID
    status: str


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


def process_ingestion_run(db: Session, run_id: UUID ):
    run = db.get(IngestionRun, run_id)

    if run is None:
        return

    try:
        run.status = IngestionStatus.PROCESSING
        run.started_at = datetime.now(timezone.utc)
        db.commit()

        raw_content, final_url, content_type = download_document(run.document_url)

        extracted = extract_document(
            raw_content=raw_content,
            source_url=final_url,
            content_type=content_type
        )

        raw_storage_path = save_raw_content(
            run_id,
            raw_content,
            content_type
            )

        

        document = Document(
            canonical_url=extracted.source_url,
            source_type=extracted.content_type,
            content_hash=content_hash(extracted.text),
            raw_storage_path=raw_storage_path,
            title=extracted.title,
            published_at=extracted.published_at,
            cleaned_text=extracted.text,
            sector=None,
        )

        db.add(document)
        db.flush()


        chunk_drafts = draft_chunk_records(document.cleaned_text)

        if not chunk_drafts:
            raise ValueError("The document produced no meaningful chunks.")


        chunk_rows = [
            DocumentChunk(
                document_id=document.id,
                page_number=chunk.page_no,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                section_heading=

            ) for chunk in chunk_drafts

        ] 

        run.status = IngestionStatus.COMPLETED
        run.completed_at = datetime.now(timezone.utc)
        run.document = document
        
        db.commit()

    except ExtractionError as exc:
        db.rollback()

        run = db.get(IngestionRun, run_id)
        run.status = IngestionStatus.FAILED
        run.created_at = datetime.now(timezone.utc)
        run.error_code = "EXTRACTION_FAILED"
        run.error_message = str(exc)
        db.commit()

    except httpx.HTTPError:
            db.rollback()
    
            run = db.get(IngestionRun, run_id)
            run.status = IngestionStatus.FAILED
            run.created_at = datetime.now(timezone.utc)
            run.error_code = "DOWNLOAD_FAILED"
            run.error_message = "The source document could not be downloaded."
            db.commit()


@router.post("/v1/documents/ingest", response_model=IngestionUrlResponse)
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

    run = IngestionRun(document_url=str(payload.url))

    db.add(run)
    db.commit()
    db.refresh(run)

    process_ingestion_run(db, run.ingestion_id)

    return run




@router.get(
    "/v1/ingestion-runs/{run_id}", response_model=IngestionUrlResponse
    )
def get_ingestion_run(
    run_id: UUID,
    response: Response,  
    db: Session = Depends(get_db)
    ):
    run = db.get(IngestionRun, run_id)

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion run not found.",
        )

    return IngestionUrlResponse(
        ingestion_id=run.ingestion_id,
        document_url=run.document_url,
        status=run.status.value,
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        
    )

