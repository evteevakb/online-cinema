"""
OpenAPI schema definitions for the persons endpoint.
"""

from typing import Any, ClassVar

from pydantic import BaseModel

from api.v1.response_models import Person, PersonFilm, PersonRole
from openapi.films import _FilmSuccessResponse


class _PersonResponseContent(BaseModel):
    """Provides example data structure for successful person list responses."""

    example: list[Person] = [
        Person(
            uuid="9755a124-665a-47fa-80f8-e156153d6a3b",
            full_name="Richard Flournoy",
            films=[
                PersonFilm(
                    uuid="65fec30e-43e2-4184-ab90-1985442415dd",
                    roles=[
                        PersonRole.WRITER,
                    ],
                ),
            ],
        ),
        Person(
            uuid="199e1dcf-eb83-48f9-9769-f601c86d4d54",
            full_name="Bethany Richards",
            films=[
                PersonFilm(
                    uuid="fceabcf0-9879-4c76-9ad8-576802df33ff",
                    roles=[
                        PersonRole.ACTOR,
                    ],
                ),
            ],
        ),
    ]


class _PersonSuccessResponse(BaseModel):
    """Schema for successful person-related API responses."""

    description: str = "A list of persons successfully retrieved"
    content: dict[str, _PersonResponseContent] = {
        "application/json": _PersonResponseContent()
    }


class _PersonDetailsResponseContent(BaseModel):
    """Provides example data structure for successful person detail responses."""

    example: Person = Person(
        uuid="9755a124-665a-47fa-80f8-e156153d6a3b",
        full_name="Richard Flournoy",
        films=[
            PersonFilm(
                uuid="65fec30e-43e2-4184-ab90-1985442415dd",
                roles=[
                    PersonRole.WRITER,
                ],
            ),
        ],
    )


class _PersonDetailsSuccessResponse(BaseModel):
    """Schema for successful person detail responses."""

    description: str = "Person details successfully retrieved"
    content: dict[str, _PersonDetailsResponseContent] = {
        "application/json": _PersonDetailsResponseContent()
    }


class _PersonDetailsNotFoundResponse(BaseModel):
    """Schema for 404 responses when a person is not found."""

    description: str = "Person not found"
    content: dict[str, dict[str, Any]] = {
        "application/json": {
            "example": {
                "detail": "Person with UUID 025c58cd-1b7e-43be-9ffb-8571a613579b not found"
            }
        }
    }


class PersonDetails(BaseModel):
    """OpenAPI schema for the person detail endpoint."""

    summary: ClassVar[str] = "Get details of a person by UUID"
    description: ClassVar[str] = (
        "Retrieve detailed information about a specific person using their UUID."
    )
    response_description: ClassVar[str] = (
        "A person object containing an UUID, full name and a list of their films."
    )
    responses: ClassVar[dict[int, dict]] = {
        200: _PersonDetailsSuccessResponse().model_dump(),
        404: _PersonDetailsNotFoundResponse().model_dump(),
    }


class PersonsSearch(BaseModel):
    """OpenAPI schema for the persons search endpoint."""

    summary: ClassVar[str] = "Search for a person"
    description: ClassVar[str] = "Retrieve a list of persons using search."
    response_description: ClassVar[str] = (
        "A person object containing an UUID, full name, and a list of their films."
    )
    responses: ClassVar[dict[int, dict]] = {
        200: _PersonSuccessResponse().model_dump(),
    }


class PersonFilms(BaseModel):
    """OpenAPI schema for the person films endpoint."""

    summary: ClassVar[str] = "Retrieve films associated with a person."
    description: ClassVar[str] = (
        "Fetches a list of films in which the specified person has participated."
    )
    response_description: ClassVar[str] = (
        " A list of films associated with the person with film's UUID, title, and IMDb rating."
    )
    responses: ClassVar[dict[int, dict]] = {
        200: _FilmSuccessResponse().model_dump(),
    }


__all__ = ["PersonFilms", "PersonDetails", "PersonsSearch"]
