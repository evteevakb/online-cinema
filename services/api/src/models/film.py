"""
Contains classes that describe the business entity of a movie.
"""

from pydantic import BaseModel

from models.genre import Genre
from models.person import PersonBase


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float | None = None
    description: str | None = None
    genres: list[Genre] = []
    actors: list[PersonBase] = []
    directors: list[PersonBase] = []
    writers: list[PersonBase] = []


class FilmBase(BaseModel):
    id: str
    title: str
    imdb_rating: float | None = None
