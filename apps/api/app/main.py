from uuid import UUID, uuid4

from fastapi import FastAPI, Response, status
from pydantic import AnyHttpUrl, BaseModel

app = FastAPI(
    title="RegIntel API",
    version="0.1.0",
    description="Traceable regulatory intelligence for UK consumer-credit firms.",
)


class HealthResponse(BaseModel):
    status: str


class IngestionUrlResponse(BaseModel):
    ingestion_id: UUID | None = None
    status: str


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/v1/documents/ingest")
def UrlStatus(url: AnyHttpUrl, response: Response) -> IngestionUrlResponse:

    allowed_hosts={
        'fca.org.uk', 
        'register.fca.org.uk',
        'handbook.fca.org.uk',
        'www.fca.org.uk', 
        'www.register.fca.org.uk',
        'www.handbook.fca.org.uk'
        }

    if url.host not in allowed_hosts:
        response.status_code=status.HTTP_400_BAD_REQUEST

        return IngestionUrlResponse(status="Rejected - Not an FCA Url")

    response.status_code=status.HTTP_202_ACCEPTED

    return IngestionUrlResponse(ingestion_id=uuid4(), status="Queued")


@app.get("/v1/ingestion-runs/{run_id}")
    
        
    
    

    

