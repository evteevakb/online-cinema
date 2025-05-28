# Deploy ETL for events service

For service description see [README](../../services/events_etl/README.md).

## Setting up environment variables

Before running the project, you need to modify `config.xml` and `users.xml` files based on the provided file templates in `configs` directory of the current folder.

## Running

Once the `.xml` files for ClickHouse nodes configuration are set up, go back to the folder `events_etl` and run the following command to start all components:

    docker-compose -f docker-compose.local.yml up --build

The API is available now at `localhost:83`. User interface for Kafka is available at `localhost:8081`.
