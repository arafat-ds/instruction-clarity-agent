"""
routes/health.py — GET /health and GET /ready
"""

import os

from fastapi import APIRouter

from api.core.config import get_settings
from api.schemas.response import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service name and version. Always 200 if the service is running.",
)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", version=settings.app_version)


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness check",
    description="Checks whether required environment variables are configured.",
)
def ready() -> ReadyResponse:
    gemini_configured = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    return ReadyResponse(ready=gemini_configured, gemini_configured=gemini_configured)
