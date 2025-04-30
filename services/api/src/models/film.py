"""
Contains classes that describe the business entity of a movie.
"""
from datetime import date

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
    creation_data: date | None = None
    paid_only: bool = False


class FilmBase(BaseModel):
    id: str
    title: str
    imdb_rating: float | None = None
