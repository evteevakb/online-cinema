"""
Contains classes that describe the business entity of a person.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel


class PersonRole(str, Enum):
    ACTOR = "actor"
    DIRECTOR = "director"
    WRITER = "writer"


class PersonBase(BaseModel):
    id: str
    name: str


class FilmPerson(BaseModel):
    id: str
    roles: List[str] = []


class Person(PersonBase):
    films: List[FilmPerson]
