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

Once the `.env` files are set up, go to the root folder (`auth`) and run the following command to create external network (if not created) and start all components:

    docker network create shared_network
    docker-compose up --build -d

The service now is available at `localhost:81`.

## Creating superuser

Commands to create superuser:
    
    docker exec -it auth bash
    python3 create_superuser.py admin@test.com 1234


## Testing

To run the functional tests, follow these steps:

### Step 1: Create .env files
Prepare the required environment files based on the examples in the `tests/functional/envs/` directory.

For each `.test.env.example` file, create a corresponding `.test.env` file with the necessary environment variables. For example:


    cp tests/functional/envs/.redis.test.env.example tests/functional/envs/.redis.test.env


### Step 2: Build Docker image (if needed)
Ensure the `auth:latest` Docker image exists locally. If it's not available, build it from the project root:

    docker-compose build

### Step 3: Launch the test environment

Navigate to the test directory and start the containers required for testing:

    cd tests/functional
    docker-compose -f test.docker-compose.yml up --build -d

### Step 4: Check test results

The results of the functional tests will be shown in the logs of the `auth-functional-tests` container.

## Service schema

[Schema](https://miro.com/welcomeonboard/R0F6RmtPWVFlNUJ2eitsVHRCMTZ2YVN0SHp3ay9TWCtIR2JEOW5Pelo0cEFRUUFjZklWKy96dTBZL0I0UG5rVDVzOEhQZlVrelpyZEcveDUxUklSc0V0Vno0SnVNRDdKNTdUTWVhZXlHSUtXQ1FaYXNpUzJSVU9OeDdyWDFhOEJBS2NFMDFkcUNFSnM0d3FEN050ekl3PT0hdjE=?share_link_id=611276372820)

## Contributors

- [@Escros1](https://github.com/Escros1)
- [@evteevakb](https://github.com/evteevakb)
- [@IstyxI](https://github.com/IstyxI)
- [@wegas66](https://github.com/wegas66)
