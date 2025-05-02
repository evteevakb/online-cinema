"""
OpenAPI schema definitions for the films endpoint.
"""

from typing import Any, ClassVar

from pydantic import BaseModel

from api.v1.response_models import Film, FilmBase, GenreBase, PersonBase


class _FilmResponseContent(BaseModel):
    """Provides example data structure for successful film list responses."""

    example: list[FilmBase] = [
        FilmBase(
            uuid="025c58cd-1b7e-43be-9ffb-8571a613579b",
            title="Star Wars: Episode VI - Return of the Jedi",
            imdb_rating=8.3,
        ),
        FilmBase(
            uuid="0312ed51-8833-413f-bff5-0e139c11264a",
            title="Star Wars: Episode V - The Empire Strikes Back",
            imdb_rating=8.7,
        ),
    ]


class _FilmDetailsResponseContent(BaseModel):
    """Provides example data structure for successful film detail responses."""

    example: Film = Film(
        uuid="025c58cd-1b7e-43be-9ffb-8571a613579b",
        title="Star Wars: Episode VI - Return of the Jedi",
        imdb_rating=8.3,
        description="Luke Skywalker battles horrible Jabba the Hut and cruel Darth Vader to save his comrades in the Rebel Alliance and triumph over the Galactic Empire. Han Solo and Princess Leia reaffirm their love and team with Chewbacca, Lando Calrissian, the Ewoks and the androids C-3PO and R2-D2 to aid in the disruption of the Dark Side and the defeat of the evil emperor.",
        genres=[
            GenreBase(uuid="120a21cf-9097-479e-904a-13dd7198c1dd", name="Adventure"),
            GenreBase(uuid="3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", name="Action"),
        ],
        actors=[
            PersonBase(
                uuid="26e83050-29ef-4163-a99d-b546cac208f8", full_name="Mark Hamill"
            ),
            PersonBase(
                uuid="5b4bf1bc-3397-4e83-9b17-8b10c6544ed1", full_name="Harrison Ford"
            ),
        ],
        directors=[
            PersonBase(
                uuid="3214cf58-8dbf-40ab-9185-77213933507e",
                full_name="Richard Marquand",
            ),
        ],
        writers=[
            PersonBase(
                uuid="3217bc91-bcfc-44eb-a609-82d228115c50", full_name="Lawrence Kasdan"
            ),
            PersonBase(
                uuid="a5a8f573-3cee-4ccc-8a2b-91cb9f55250a", full_name="George Lucas"
            ),
        ],
    )


class _FilmSuccessResponse(BaseModel):
    """Schema for successful film-related API responses."""

    description: str = "A list of films successfully retrieved"
    content: dict[str, _FilmResponseContent] = {
        "application/json": _FilmResponseContent()
    }


class _FilmDetailsSuccessResponse(BaseModel):
    """Schema for successful film detail responses."""

    description: str = "Film details successfully retrieved"
    content: dict[str, _FilmDetailsResponseContent] = {
        "application/json": _FilmDetailsResponseContent()
    }


class _FilmDetailsNotFoundResponse(BaseModel):
    """Schema for 404 responses when a film is not found."""

    description: str = "Film not found"
    content: dict[str, dict[str, Any]] = {
        "application/json": {
            "example": {
                "detail": "Film with UUID 025c58cd-1b7e-43be-9ffb-8571a613579b not found"
            }
        }
    }


class Films(BaseModel):
    """OpenAPI schema for the fil,s list endpoint."""

    summary: ClassVar[str] = "Get a list of films"
    description: ClassVar[str] = "Retrieve a paginated list of films."
    response_description: ClassVar[str] = (
        "A list of films, each containing an UUID, title, and rating."
    )
    responses: ClassVar[dict[int, dict]] = {200: _FilmSuccessResponse().model_dump()}


class FilmDetails(BaseModel):
    """OpenAPI schema for the film detail endpoint."""

    summary: ClassVar[str] = "Get details of a film by UUID"
    description: ClassVar[str] = (
        "Retrieve detailed information about a specific film using its UUID."
    )
    response_description: ClassVar[str] = (
        "A film object containing an UUID, title, rating, description and lists of genres, actors, directors, and writers."
    )
    responses: ClassVar[dict[int, dict]] = {
        200: _FilmDetailsSuccessResponse().model_dump(),
        404: _FilmDetailsNotFoundResponse().model_dump(),
    }


class FilmsSearch(BaseModel):
    """OpenAPI schema for the films search endpoint."""

    summary: ClassVar[str] = "Search for a film"
    description: ClassVar[str] = "Retrieve a list of films using search."
    response_description: ClassVar[str] = (
        "A film object containing an UUID, title, and rating."
    )
    responses: ClassVar[dict[int, dict]] = {
        200: _FilmSuccessResponse().model_dump(),
    }


__all__ = ["Films", "FilmDetails", "FilmsSearch"]
