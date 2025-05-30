# Deploy ETL for events service

For service description see [README](../../services/events_etl/README.md).

## Setting up config variables

Before running the project, you need to create `.xml` files based on the provided `.xml.example` templates in `configs` directory of the current folder.

Navigate to the `configs` directory and create the required `.xml` files:

    cp ./clickhouse-node-1/.config.xml.example ./clickhouse-node-1/.config.xml
    cp ./clickhouse-node-1/.users.xml.example ./clickhouse-node-1/.users.xml
    ...

Open each `.xml` file and update the necessary values.

## Running

Once the `.xml` files for ClickHouse nodes configuration are set up, go back to the folder `events_etl` and run the following command to start all components:

    docker-compose -f docker-compose.local.yml up --build

The API is available now at `localhost:83`. User interface for Kafka is available at `localhost:8081`.
