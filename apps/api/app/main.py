
from fastapi import FastAPI
from pydantic import BaseModel

from apps.api.app.answer import router as answer_router
from apps.api.app.services.ingestion import router

app = FastAPI(
    title="RegIntel API",
    version="0.1.0",
    description="Traceable regulatory intelligence for UK consumer-credit firms.",
)

app.include_router(router)
app.include_router(answer_router)

class HealthResponse(BaseModel):
    status: str


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")



    
        
    
    

    

