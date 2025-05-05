# Deploy admin panel, API and auth services for the online cinema

For services description see:
- [admin service README](../../services/admin/README.md);
- [api service README](../../services/api/README.md);
- [auth service README](../../services/auth/README.md).

## Installation

### Setting up environment variables

Before running the project, you need to create `.env` files based on the provided `.env.example` templates in `local/envs` directory of the current folder and of the `../admin` and `../api/local` folders.

#### Step 1: Create .env files

Navigate to the `local/envs` directory and create the required `.env` files:

    cp .db.env.example .db.env
    cp .redis.env.example .redis.env
    cp .service.env.example .service.env

#### Step 2: Fill in the .env files

Open each `.env` file and update the necessary values.

##### .db.env

    POSTGRES_DB=test_database  # must be equal to a database name
    POSTGRES_USER=app  # can be modified
    POSTGRES_PASSWORD=test_password  # can be modified
    POSTGRES_HOST=auth-db  # must be equal to a container name
    POSTGRES_PORT=5432  # must be equal to a standard PostgreSQL port
    POSTGRES_ECHO=True  # True for showing logs, otherwise False

##### .redis.env

    REDIS_PASSWORD=redis_password  # can be modified
    REDIS_USER_NAME=user  # can be modified
    REDIS_USER_PASSWORD=user_password  # can be modified
    REDIS_HOST=auth-redis  # must be equal to container name
    REDIS_PORT=6379  # must be equal to the default Redis port

##### .service.env

    API_PROJECT_NAME=auth-service  # can be modified
    API_HOST=0.0.0.0  # must be equal to FastAPI app host 
    API_CONTAINER_NAME=auth  # must be equal to container name
    API_PORT=8000  # must be equal to FastAPI app port 

## Running

Once the `.env` files are set up, go to the folder `auth/local` and run the following command to start all components:

    docker-compose -f docker-compose.local.yml up --build

The `admin` service now is available at `localhost:80`, `api` - at `localhost:81` and several API endpoints of `auth` service - at `localhost:82`. Available for users `auth` endpoints are the following:

- `api/v1/profile`
- `api/v1/auth/registration`
- `api/v1/auth/login`
- `api/v1/auth/logout`
- `api/openapi`

## Testing

To run the functional tests, follow these steps:

### Step 1: Create .env files

Prepare the required environment files based on the examples in the `test/envs/` directory.

For each `.test.env.example` file, create a corresponding `.test.env` file with the necessary environment variables. For example:


    cp test/envs/.redis.test.env.example test/envs/.redis.test.env


### Step 2: Build Docker image (if needed)
Ensure the `auth:latest` Docker image exists locally. If it's not available, build it from the `../local` folder:

    docker-compose -f docker-compose.local.yml --build

### Step 3: Launch the test environment

Navigate to the test directory and start the containers required for testing:

    docker-compose -f docker-compose.test.yml up --build

### Step 4: Check test results

The results of the functional tests will be shown in the logs of the `auth-functional-tests` container.