"""
OpenAPI schema definitions for the genres endpoint.
"""

from typing import Any, ClassVar

from pydantic import BaseModel

from api.v1.response_models import GenreBase


class _GenreResponseContent(BaseModel):
    """Provides example data structure for successful genre list responses."""

    example: list[GenreBase] = [
        GenreBase(uuid="3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", name="Action"),
        GenreBase(uuid="120a21cf-9097-479e-904a-13dd7198c1dd", name="Comedy"),
    ]


class _GenreDetailsResponseContent(BaseModel):
    """Provides example data structure for successful genre detail responses."""

    example: GenreBase = GenreBase(
        uuid="3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", name="Action"
    )


class _GenreSuccessResponse(BaseModel):
    """Schema for successful genre-related API responses."""

    description: str = "A list of genres successfully retrieved"
    content: dict[str, _GenreResponseContent] = {
        "application/json": _GenreResponseContent()
    }


class _GenreDetailsSuccessResponse(BaseModel):
    """Schema for successful genre detail responses."""

    description: str = "Genre details successfully retrieved"
    content: dict[str, _GenreDetailsResponseContent] = {
        "application/json": _GenreDetailsResponseContent()
    }


class _GenreDetailsNotFoundResponse(BaseModel):
    """Schema for 404 responses when a genre is not found."""

    description: str = "Genre not found"
    content: dict[str, dict[str, Any]] = {
        "application/json": {
            "example": {
                "detail": "Genre with UUID 3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff not found"
            }
        }
    }


class Genres(BaseModel):
    """OpenAPI schema for the genres list endpoint."""

    summary: ClassVar[str] = "Get a list of genres"
    description: ClassVar[str] = "Retrieve a paginated list of genres."
    response_description: ClassVar[str] = (
        "A list of genres, each containing an UUID and a name."
    )
    responses: ClassVar[dict[int, dict]] = {200: _GenreSuccessResponse().model_dump()}


class GenreDetails(BaseModel):
    """OpenAPI schema for the genre detail endpoint."""

    summary: ClassVar[str] = "Get details of a genre by UUID"
    description: ClassVar[str] = (
        "Retrieve detailed information about a specific genre using its UUID."
    )
    response_description: ClassVar[str] = (
        "A genre object containing an UUID and a name."
    )
    responses: ClassVar[dict[int, dict]] = {
        200: _GenreDetailsSuccessResponse().model_dump(),
        404: _GenreDetailsNotFoundResponse().model_dump(),
    }


__all__ = ["Genres", "GenreDetails"]
