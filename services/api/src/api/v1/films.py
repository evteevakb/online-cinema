from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.response_models import Film, PersonBase, GenreBase, FilmBase
from openapi.films import FilmDetails, FilmsSearch, Films
from services.film import FilmService, get_film_service, film_filters
from utils.auth import Authorization, Roles

router = APIRouter()


@router.get(
    "/search",
    response_model=List[FilmBase],
    summary=FilmsSearch.summary,
    description=FilmsSearch.description,
    response_description=FilmsSearch.response_description,
    responses=FilmsSearch.responses,
)
async def films_search(
    query: str,
    common_filters: dict = Depends(film_filters),
    film_service: FilmService = Depends(get_film_service),
    user_roles=Depends(Authorization(allowed_roles=[Roles.ADMIN, Roles.SUPERUSER, Roles.USER, Roles.PAID_USER]))
) -> List[FilmBase]:
    films = await film_service.get_all(query=query, **common_filters)
    return [
        FilmBase(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]


@router.get(
    "/{film_uuid}",
    response_model=Film,
    summary=FilmDetails.summary,
    description=FilmDetails.description,
    response_description=FilmDetails.response_description,
    responses=FilmDetails.responses,
)
async def film_details(
    film_uuid: str,
    film_service: FilmService = Depends(get_film_service),
    user_roles=Depends(Authorization(allowed_roles=[Roles.ADMIN, Roles.SUPERUSER, Roles.USER, Roles.PAID_USER]))
) -> Film:
    film = await film_service.get_by_uuid(film_uuid=film_uuid, user_roles=user_roles)

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Film with UUID {film_uuid} not found",
        )

    actors = [PersonBase(uuid=actor.id, full_name=actor.name) for actor in film.actors]
    writers = [
        PersonBase(uuid=writer.id, full_name=writer.name) for writer in film.writers
    ]
    directors = [
        PersonBase(uuid=director.id, full_name=director.name)
        for director in film.directors
    ]

    genres = [GenreBase(uuid=genre.id, name=genre.name) for genre in film.genres]

    return Film(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=genres,
        actors=actors,
        directors=directors,
        writers=writers,
    )


@router.get(
    "",
    response_model=List[FilmBase],
    summary=Films.summary,
    description=Films.description,
    response_description=Films.response_description,
    responses=Films.responses,
)
async def films_list(
    common_filters: dict = Depends(film_filters),
    film_service: FilmService = Depends(get_film_service),
    user_roles=Depends(Authorization(allowed_roles=[Roles.ADMIN, Roles.SUPERUSER, Roles.USER, Roles.PAID_USER]))
) -> List[FilmBase]:
    films = await film_service.get_all(**common_filters)
    results = []
    if films:
        results = [
            FilmBase(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
            for film in films
        ]
    return results
