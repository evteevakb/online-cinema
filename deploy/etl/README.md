# Deploy ETL process for transferring data from PostgreSQL to Elasticsearch

For service description see [service README](../../services/etl/README.md).

## Installation

Before setting up the ETL process, make sure to configure the admin panel as described in [admin deploy README](../admin/README.md).

### Setting up environment variables

Before running the project, you need to create `.env` files based on the provided `.env.example` templates in `envs` directory.

#### Step 1: Create .env files

Navigate to the `envs` directory and create the required `.env` files:

    cp .elastic.env.example .elastic.env
    cp .etl.env.example .etl.env
    cp .redis.env.example .redis.env

#### Step 2: Fill in the .env files

Open each `.env` file and update the necessary values.

##### .elastic.env

    ELASTIC_USER=elastic  # can be modified
    ELASTIC_PASSWORD=strong_password  # can be modified
    ELASTIC_HOST=elasticsearch  # must be equal to Elasticsearch container name
    ELASTIC_PORT=9200  # must be equal to the default Elasticsearch port

##### .etl.env

    ETL_INDEX="movies"  # name of the Elasticsearch index where the data will be stored
    ETL_INDEX_SCHEMA_FILEPATH="movies_schema.json"  # file path to the JSON schema that defines the structure of the Elasticsearch index
    ETL_LIMIT=2  # maximum number of records to process in a single batch during the ETL process
    ETL_MIN_TIMESTAMTZ="2020-01-01 00:00:00.000 +0200"  #  minimum timestamp (in a specific timezone) from which the ETL process should start extracting data
    ETL_SLEEP_INTERVAL_SEC=60  # interval (in seconds) for the ETL process to sleep between consecutive runs
    ETL_TIMESTAMPTZ_FORMAT="%Y-%m-%d %H:%M:%S.%f %z"  # format string for parsing and formatting timestamps with timezone information
    ETL_TIMEZONE_HOURS=2  # timezone offset (in hours) to be applied to timestamps during the ETL process

##### .redis.env

    REDIS_PASSWORD=redis_password  # can be modified
    REDIS_USER_NAME=user  # can be modified
    REDIS_USER_PASSWORD=user_password  # can be modified
    REDIS_HOST=admin-redis  # must be equal to container name
    REDIS_PORT=6379  # must be equal to the default Redis port

## Running

Once the `.env` files are set up, go to the folder `etl` and run the following command to start all components:

    docker-compose -f docker-compose.local.yml up --build
