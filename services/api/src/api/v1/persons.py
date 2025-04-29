from http import HTTPStatus
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from api.v1.response_models import PersonFilm, Person, FilmBase
from openapi.persons import PersonDetails, PersonFilms, PersonsSearch
from services.person import PersonService, get_person_service, person_filters
from utils.auth import Authorization, Roles

router = APIRouter()


@router.get(
    "/search",
    response_model=List[Person],
    summary=PersonsSearch.summary,
    description=PersonsSearch.description,
    response_description=PersonsSearch.response_description,
    responses=PersonsSearch.responses,
)
async def search_persons(
    query: str,
    common_filters: dict = Depends(person_filters),
    service: PersonService = Depends(get_person_service),
    _=Depends(
        Authorization(
            allowed_roles=[Roles.ADMIN, Roles.SUPERUSER, Roles.USER, Roles.PAID_USER]
        )
    ),
) -> list[Person]:
    persons = await service.search_persons(query=query, **common_filters)
    return [
        Person(
            uuid=person.id,
            full_name=person.name,
            films=[PersonFilm(uuid=film.id, roles=film.roles) for film in person.films],
        )
        for person in persons
    ]


@router.get(
    "/{person_uuid}",
    response_model=Person,
    summary=PersonDetails.summary,
    description=PersonDetails.description,
    response_description=PersonDetails.response_description,
    responses=PersonDetails.responses,
)
async def person_details(
    person_uuid: str,
    person_service: PersonService = Depends(get_person_service),
    _=Depends(
        Authorization(
            allowed_roles=[Roles.ADMIN, Roles.SUPERUSER, Roles.USER, Roles.PAID_USER]
        )
    ),
) -> Person:
    person = await person_service.get_person(person_uuid)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Person with UUID {person_uuid} not found",
        )

    return Person(
        uuid=person.id,
        full_name=person.name,
        films=[PersonFilm(uuid=film.id, roles=film.roles) for film in person.films],
    )


@router.get(
    "/{person_uuid}/film/",
    response_model=List[FilmBase],
    summary=PersonFilms.summary,
    description=PersonFilms.description,
    response_description=PersonFilms.response_description,
    responses=PersonFilms.responses,
)
async def person_films(
    person_uuid: str,
    person_service: PersonService = Depends(get_person_service),
    _=Depends(
        Authorization(
            allowed_roles=[Roles.ADMIN, Roles.SUPERUSER, Roles.USER, Roles.PAID_USER]
        )
    ),
) -> list[FilmBase]:
    films = await person_service.get_films_by_person(person_uuid)
    return [
        FilmBase(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
