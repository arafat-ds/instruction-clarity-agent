"""
schemas/response.py — Pydantic models for API responses.
"""

from typing import Optional
from pydantic import BaseModel


class AgentResponse(BaseModel):
    status: str
    actions: list[str]
    deadline: Optional[str]
    priority: Optional[str]
    clarifications: list[str]


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadyResponse(BaseModel):
    ready: bool
    gemini_configured: bool


class ErrorDetail(BaseModel):
    message: str
    code: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
