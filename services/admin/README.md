# Admin panel for online cinema

The `admin` service provides an administrative interface for managing the online cinema platform. It allows administrators to manage movies, genres, and other related entities.

## `/admin` endpoint

The `/admin` endpoint provides access to the Django admin panel for managing the backend data. Administrators can log in to this interface to perform CRUD operations on movies, genres, and other entities.

## API Endpoints

### `GET /api/v1/movies`

Retrieves a paginated list of movies.

**Parameters**:
  - `page` (optional): The page number to retrieve.

### `GET /api/v1/movies/{id}`

Retrieves detailed information about a specific movie by its UUID.

**Parameters**:
  - `id` (required): The UUID of the movie.

## OpenAPI

The `admin` service includes Swagger OpenAPI documentation for all available API endpoints at `api/openapi`.

## Running

To start the `admin` service, follow the instructions in the [deployment documentation](../../deploy/sprint_2/README.md).

## Tests

To run the Postman tests:
1. Import the `postman_tests.json` file located in the `tests` directory into Postman.
2. Configure the required environment variables in Postman.
3. Execute the collection to verify the API functionality.
