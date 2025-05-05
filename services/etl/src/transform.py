"""
Provides functionality for transforming raw data from PostgreSQL into a format suitable for Elasticsearch.
"""

from collections import defaultdict
from typing import Any, Optional
from uuid import UUID
from datetime import date, datetime, timedelta

from pydantic import BaseModel, Field, field_validator, computed_field

roles = {"actor", "director", "writer"}


class PersonPostgres(BaseModel):
    """Represents a person's data as loaded from PostgreSQL."""

    person_id: str
    person_name: str
    person_role: str


class GenresPostgres(BaseModel):
    """Represents a genre data as loaded from PostgreSQL."""

    genre_id: str
    genre_name: str


class FilmworkPostgres(BaseModel):
    """Represents a filmwork's data as loaded from PostgreSQL."""

    fw_id: str
    title: str
    description: Optional[str]
    rating: Optional[float]
    persons: list[PersonPostgres] = []
    genres: list[GenresPostgres] = []
    creation_date: date | None

    @computed_field
    @property
    def paid_only(self) -> bool:
        """Checks whether content is available via subscription."""
        if self.creation_date is not None:
            three_years = timedelta(days=3*365)
            return datetime.now().date() - self.creation_date < three_years
        return False

    @field_validator("fw_id", mode="before")
    @classmethod
    def parse_uuid(cls, value: str | UUID) -> str:
        """Converts a UUID to a string if necessary.

        Args:
            value: UUID or string representation of the filmwork ID.

        Returns:
            A string representation of the filmwork ID.
        """
        if isinstance(value, UUID):
            return str(value)
        return value


class PersonElastic(BaseModel):
    """Represents a person's data as will be stored in Elasticsearch."""

    id: str
    name: str


class GenreElastic(BaseModel):
    """Represents a ganre data as will be stored in Elasticsearch."""

    id: str = Field(alias="genre_id")
    name: str = Field(alias="genre_name")


class FilmworkElastic(BaseModel):
    """Represents a filmwork's data as will be stored in Elasticsearch."""

    id: str = Field(alias="fw_id")
    imdb_rating: Optional[float] = Field(alias="rating")
    genres: list[GenreElastic] = []
    title: str
    description: Optional[str]
    directors_names: list[str] = []
    actors_names: list[str] = []
    writers_names: list[str] = []
    directors: list[PersonElastic] = []
    actors: list[PersonElastic] = []
    writers: list[PersonElastic] = []
    creation_date: date | None
    paid_only: bool


def transform_postgres_to_elastic(
    row: dict[str, Any],
) -> dict[str, Any]:
    """Transforms raw PostgreSQL data into a format suitable for Elasticsearch.

    Args:
        row: a dictionary representing a single row of PostgreSQL data.

    Returns:
        A dictionary representing the transformed data, ready for Elasticsearch.
    """
    role_mapping = defaultdict(list)
    grouped_roles = defaultdict(list)

    postgres_row = FilmworkPostgres(**row)
    elastic_row = FilmworkElastic(**postgres_row.model_dump())

    for person in postgres_row.persons:
        if person.person_role in roles:
            role_mapping[person.person_role].append(person.person_name)
            grouped_roles[person.person_role].append(
                {"id": person.person_id, "name": person.person_name}
            )

    for role in roles:
        setattr(elastic_row, f"{role}s_names", role_mapping[role])
        setattr(
            elastic_row,
            f"{role}s",
            [PersonElastic(**person) for person in grouped_roles[role]],
        )

    return elastic_row.model_dump()
