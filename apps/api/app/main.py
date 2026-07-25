from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="RegIntel API",
    version="0.1.0",
    description="Traceable regulatory intelligence for UK consumer-credit firms.",
)


class HealthResponse(BaseModel):
    status: str


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")
