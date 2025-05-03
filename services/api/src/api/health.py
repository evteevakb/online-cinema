"""
Health check module for the FastAPI application.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get(
    "",
    summary="Health Check",
    description="Returns the health status of the application.",
    response_description="A JSON object indicating service status.",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {"application/json": {"example": {"status": "ok"}}},
        }
    },
)
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict[str, str]: a JSON response indicating the service status.
    """
    return {"status": "ok"}
