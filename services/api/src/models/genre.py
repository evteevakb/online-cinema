"""
Contains classes that describe the business entity of a genre.
"""

from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    name: str
