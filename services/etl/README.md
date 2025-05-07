# ETL Service

This ETL (Extract, Transform, Load) service is designed to transfer data from a PostgreSQL database to an Elasticsearch instance. It extracts data, transforms it into the required format, and loads it into Elasticsearch for further use in fulltext search.

## Running

To start the `etl` service, follow the instructions in the [deployment documentation](../../deploy/etl/README.md).

## Tests

To run the Postman tests:
1. Import the `postman_tests.json` file located in the `tests` directory into Postman.
2. Configure the required environment variables in Postman.
3. Execute the collection to verify the functionality.
