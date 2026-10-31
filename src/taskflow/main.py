from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TaskFlow API")


class HealthResponse(BaseModel):
    status: Literal["ok"]


@app.get(
    "/health",
    operation_id="healthCheck",
    response_model=HealthResponse,
    tags=["Health"],
)
def health_check() -> HealthResponse:
    """Report API liveness without touching PostgreSQL."""
    return HealthResponse(status="ok")
