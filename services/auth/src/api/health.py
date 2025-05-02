"""
Health check module for the FastAPI application.
"""

from fastapi import APIRouter

from openapi.health import Health

router = APIRouter()


@router.get(
    "",
    summary=Health.summary,
    description=Health.description,
    response_description=Health.response_description,
    responses=Health.responses,
)
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict[str, str]: a JSON response indicating the service status.
    """
    return {"status": "ok"}
