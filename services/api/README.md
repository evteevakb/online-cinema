# Asynchronous API for a cinema

This service provides an asynchronous API for managing and retrieving cinema-related data, including films, genres, and persons.

## API Endpoints

- **Films**
  - `GET /api/v1/films`: Retrieve a list of films with optional filters for pagination and sorting.
  - `GET /api/v1/films/{film_uuid}`: Get detailed information about a specific film.
  - `GET /api/v1/films/search`: Search for films based on a query string.

- **Genres**
  - `GET /api/v1/genres`: Retrieve a list of genres.
  - `GET /api/v1/genres/{genre_uuid}`: Get detailed information about a specific genre.

- **Persons**
  - `GET /api/v1/persons`: Retrieve a list of persons involved in films.
  - `GET /api/v1/persons/{person_uuid}`: Get detailed information about a specific person.
  - `GET /api/v1/persons/search`: Search for persons based on a query string.

## Running

To start the `api` service, follow the instructions in the [deployment documentation](../../deploy/api/README.md).