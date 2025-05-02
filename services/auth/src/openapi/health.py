"""
OpenAPI schema definitions for the health endpoint.
"""

from typing import Any, ClassVar

from pydantic import BaseModel

__all__ = ["Health"]


class _HealthSuccessResponse(BaseModel):
    """Schema for successful health check API response."""

    description: str = "Service is healthy"
    content: dict[str, dict[str, str]] = {
        "application/json": {"status": "ok"},
    }


class Health(BaseModel):
    """OpenAPI schema for the health endpoint."""

    summary: ClassVar[str] = "Health check"
    description: ClassVar[str] = "Returns the health status of the application."
    response_description: ClassVar[str] = "A JSON object indicating service status."
    responses: ClassVar[dict[int, Any]] = {
        200: _HealthSuccessResponse().model_dump(),
    }
