# Asynchronous API for a cinema

## Installation

### Setting up environment variables

Before running the project, you need to create `.env` files based on the provided `.env.example` templates in `envs` directory.

#### Step 1: Create .env files

Navigate to the `envs` directory and create the required `.env` files:

    cp .elasticsearch.env.example .elasticsearch.env
    cp .redis.env.example .redis.env
    cp .service.env.example .src.env

#### Step 2: Fill in the .env files

Open each `.env` file and update the necessary values.

##### .elasticsearch.env

    ELASTIC_USER=elastic  # must be equal to a default Elasticsearch username
    ELASTIC_PASSWORD=strong_password  # can be modified
    ELASTIC_HOST=elasticsearch  # must be equal to a container name
    ELASTIC_PORT=9200  # must be equal to a standard Elasticsearch port


##### .redis.env

    REDIS_PASSWORD=redis_password  # can be modified
    REDIS_USER_NAME=user  # can be modified
    REDIS_USER_PASSWORD=user_password   # can be modified
    REDIS_HOST=api-redis  # must be equal to a container name
    REDIS_PORT=6379  # must be equal to a standard Redis port

##### .service.env

    API_PROJECT_NAME=movies  # can be modified
    API_HOST=0.0.0.0  # must be 0.0.0.0 to ensure accessibility by nginx
    API_CONTAINER_NAME=api  # must be equal to a container name
    API_PORT=8000  # can be modified, but do not forget to fix the port number in docker-compose container expose section for proper documentation

## Running

Once the `.env` files are set up, run the following command to start all services:

    docker-compose up --build -d

The app will be available at `localhost:80`.

## Testing

To run the functional tests, follow these steps:

### Step 1: Create .env files
Prepare the required environment files based on the examples in the `tests/functional/envs/` directory.

For each `.test.env.example` file, create a corresponding `.test.env` file with the necessary environment variables. For example:


    cp tests/functional/envs/.redis.test.env.example tests/functional/envs/.redis.test.env


### Step 2: Build Docker image (if needed)
Ensure the `api:latest` Docker image exists locally. If it's not available, build it from the project root:

    docker-compose build

### Step 3: Launch the test environment

Navigate to the test directory and start the containers required for testing:

    cd tests/functional
    docker-compose -f test.docker-compose.yml up --build -d

### Step 4: Check test results

The results of the functional tests will be shown in the logs of the `functional_tests` container.
