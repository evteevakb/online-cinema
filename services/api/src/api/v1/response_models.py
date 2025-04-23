from typing import List

from pydantic import BaseModel

from models.person import PersonRole


class GenreBase(BaseModel):
    """Model representing a genre"""

    uuid: str
    name: str


class PersonBase(BaseModel):
    """Model representing a person"""

    uuid: str
    full_name: str


class PersonFilm(BaseModel):
    """Model representing a persons' film"""

    uuid: str
    roles: List[PersonRole] = []


class Person(PersonBase):
    """Model representing a person with films"""

    films: List[PersonFilm] = []


class FilmBase(BaseModel):
    """Model representing a film"""

    uuid: str
    title: str
    imdb_rating: float | None = None


class Film(FilmBase):
    """Model representing a film with details"""

    description: str | None = None
    genres: List[GenreBase] = []
    actors: List[PersonBase] = []
    directors: List[PersonBase] = []
    writers: List[PersonBase] = []
