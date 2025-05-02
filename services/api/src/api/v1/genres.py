"""
Provides API routes for fetching genres.
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.response_models import GenreBase
from openapi.genres import GenreDetails, Genres
from services.genre import GenreService, get_genre_service
from utils.auth import Authorization, Roles

router = APIRouter()


@router.get(
    "",
    response_model=list[GenreBase],
    summary=Genres.summary,
    description=Genres.description,
    response_description=Genres.response_description,
    responses=Genres.responses,
)
async def get_genres(
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    genre_service: GenreService = Depends(get_genre_service),
    _=Depends(
        Authorization(
            allowed_roles=[Roles.ADMIN, Roles.SUPERUSER, Roles.USER, Roles.PAID_USER]
        )
    ),
) -> list[GenreBase]:
    """Fetches a paginated list of genres.

    Args:
        page_number (int): the page number for pagination, default is 1.
        page_size (int): the number of genres per page, default is 10.
        genre_service (GenreService): dependency injection for the genre service.

    Returns:
        list[GenreBase]: a list of genres with their UUIDs and names.
    """
    genres = await genre_service.get_all(
        page_size=page_size,
        page_number=page_number,
    )
    return (
        [GenreBase(uuid=genre.id, name=genre.name) for genre in genres]
        if genres
        else []
    )


@router.get(
    "/{genre_uuid}",
    response_model=GenreBase,
    summary=GenreDetails.summary,
    description=GenreDetails.description,
    response_description=GenreDetails.response_description,
    responses=GenreDetails.responses,
)
async def get_genre_details(
    genre_uuid: str,
    genre_service: GenreService = Depends(get_genre_service),
    _=Depends(Authorization(allowed_roles=[Roles.ADMIN, Roles.SUPERUSER])),
) -> GenreBase:
    """Retrieves detailed information about a genre by its UUID.

    Args:
        genre_uuid (str): the UUID of the genre to retrieve.
        genre_service (GenreService): dependency injection for the genre service.

    Returns:
        GenreBase: a GenreBase object containing the genre's UUID and name.

    Raises:
        HTTPException: if the genre is not found, a 404 error is raised.
    """
    genre = await genre_service.get_genre_by_uuid(
        genre_uuid=genre_uuid,
    )
    if genre is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Genre with UUID {genre_uuid} not found",
        )
    return GenreBase(
        uuid=genre.id,
        name=genre.name,
    )
