# Auth service

The `auth` service is responsible for handling user authentication and authorization. It includes features such as user login, registration, and token management.

## Service structure
- `envs`: contains environment variables for service components.
- `src`: contains the main application code.

## Installation

### Setting up environment variables

Before running the project, you need to create `.env` files based on the provided `.env.example` templates in `envs` directory.

#### Step 1: Create .env files

Navigate to the `envs` directory and create the required `.env` files:

    cp .db.env.example .db.env
    cp .redis.env.example .redis.env
    cp .service.env.example .service.env

#### Step 2: Fill in the .env files

Open each `.env` file and update the necessary values.

##### .db.env

    POSTGRES_DB=auth_database  # must be equal to a database name
    POSTGRES_USER=user  # can be modified
    POSTGRES_PASSWORD=password  # can be modified
    POSTGRES_HOST=auth-db  # must be equal to a container name
    POSTGRES_PORT=5432  # must be equal to a standard PostgreSQL port

##### .redis.env

    REDIS_PASSWORD=redis_password  # can be modified
    REDIS_USER_NAME=user  # can be modified
    REDIS_USER_PASSWORD=user_password   # can be modified
    REDIS_HOST=redis  # must be equal to a container name
    REDIS_PORT=6379  # must be equal to a standard Redis port

##### .service.env

    API_PROJECT_NAME=movies  # can be modified
    API_HOST=0.0.0.0  # must be 0.0.0.0
    API_CONTAINER_NAME=auth  # must be equal to a container name
    API_PORT=8000  # can be modified, but do not forget to fix the port number in docker-compose container expose section for proper documentation

## Running

Once the `.env` files are set up, go to the root folder (`auth`) and run the following command to start all components:

    docker-compose up --build -d

The service now is available at `localhost:80`.

## Contributors

- [@Escros1](https://github.com/Escros1)
- [@evteevakb](https://github.com/evteevakb)
- [@IstyxI](https://github.com/IstyxI)
- [@wegas66](https://github.com/wegas66)
