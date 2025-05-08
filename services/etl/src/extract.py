"""
Provides functionality for extracting data from PostgreSQL in batches.
"""

import logging
from typing import Any

from clients.postgres import PostgresClient
import psycopg

from utils.queries import (
    filmworks_data,
    genres_data,
    modified_ids,
    persons_data,
    related_filmworks,
)


class PostgresExtractor:
    """Extracts data from PostgreSQL in batches and handles connection failures."""

    def __init__(
        self,
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.client = PostgresClient()
        self.dsl = self.client.dsl
        self.logger = logger

    def __get_changed_ids(
        self,
        connection: psycopg.connection,
        table_name: str,
        start_timestamptz: str,
        stop_timestamptz: str,
        limit: int,
        offset: int,
    ) -> list[str]:
        """Retrieves IDs of modified records from a specified table.

        Args:
            connection: active PostgreSQL connection;
            table_name: name of the table to query;
            start_timestamptz: start timestamp for filtering modified records;
            stop_timestamptz: stop timestamp for filtering modified records;
            limit: maximum number of IDs to retrieve;
            offset: offset for pagination.

        Returns:
            A list of IDs of modified records.
        """
        rows = self.client.get_data(
            connection=connection,
            query=modified_ids.format(table_name),
            params={
                "start_timestamptz": start_timestamptz,
                "stop_timestamptz": stop_timestamptz,
                "limit": limit,
                "offset": offset,
            },
        )
        return [str(row["id"]) for row in rows]

    def __get_related_filmwork_ids(
        self,
        connection: psycopg.connection,
        table_name: str,
        related_ids: list[str],
    ) -> list[str]:
        """Retrieves IDs of filmworks related to the specified records.

        Args:
            connection: active PostgreSQL connection;
            table_name: name of the table to query (`person` or `genre`);
            related_ids: list of IDs from the specified table.

        Returns:
            A list of IDs of related filmworks.
        """
        rows = self.client.get_data(
            connection=connection,
            query=related_filmworks.format(table_name, table_name),
            params={
                "ids": related_ids,
            },
        )
        return [str(row["id"]) for row in rows]

    def __get_filmwork_data(
        self,
        connection: psycopg.connection,
        filmwork_ids: list[str],
    ) -> Any:
        """Retrieves filmwork data for the specified filmwork IDs.

        Args:
            connection: active PostgreSQL connection;
            filmwork_ids: list of filmwork IDs to retrieve.

        Returns:
            A list of dictionaries containing filmwork data.
        """
        return self.client.get_data(
            connection=connection,
            query=filmworks_data,
            params={
                "ids": filmwork_ids,
            },
        )

    def __get_person_data(
        self,
        connection: psycopg.connection,
        person_ids: list[str],
    ) -> Any:
        return self.client.get_data(
            connection=connection,
            query=persons_data,
            params={
                "ids": person_ids,
            },
        )

    def __get_genres_data(
        self,
        connection: psycopg.connection,
        genre_ids: list[str],
    ) -> Any:
        return self.client.get_data(
            connection=connection,
            query=genres_data,
            params={
                "ids": genre_ids,
            },
        )

    def extract(
        self,
        connection: psycopg.connection,
        table_name: str,
        start_timestamptz: str,
        stop_timestamptz: str,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """Extracts data from PostgreSQL in batches and yields the results.

        Args:
            connection: active PostgreSQL connection;
            table_name: name of the table to extract data from;
            start_timestamptz: timestamp to filter records from;
            stop_timestamptz: timestamp to filter records up to;
            limit: maximum number of IDs to retrieve;
            offset: offset for pagination.

        Returns:
            A list of dictionaries containing the extracted data.
        """
        ids = self.__get_changed_ids(
            connection=connection,
            table_name=table_name,
            start_timestamptz=start_timestamptz,
            stop_timestamptz=stop_timestamptz,
            limit=limit,
            offset=offset,
        )

        if table_name in ["person", "genre"]:
            ids = self.__get_related_filmwork_ids(
                connection=connection,
                table_name=table_name,
                related_ids=ids,
            )
        filmwork_data = self.__get_filmwork_data(
            connection=connection,
            filmwork_ids=ids,
        )
        self.logger.debug(
            "Following data was extracted from PostgreSQL: %s", filmwork_data
        )
        return filmwork_data


    def extract_persons(
        self,
        connection: psycopg.connection,
        table_name: str,
        start_timestamptz: str,
        stop_timestamptz: str,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        ids = self.__get_changed_ids(
            connection=connection,
            table_name=table_name,
            start_timestamptz=start_timestamptz,
            stop_timestamptz=stop_timestamptz,
            limit=limit,
            offset=offset,
        )
        persons_data = self.__get_person_data(
            connection=connection,
            person_ids=ids,
        )
        self.logger.debug(
            "Following data was extracted from PostgreSQL: %s", persons_data
        )
        return persons_data

    def extract_genres(
        self,
        connection: psycopg.connection,
        table_name: str,
        start_timestamptz: str,
        stop_timestamptz: str,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        ids = self.__get_changed_ids(
            connection=connection,
            table_name=table_name,
            start_timestamptz=start_timestamptz,
            stop_timestamptz=stop_timestamptz,
            limit=limit,
            offset=offset,
        )
        genres_data = self.__get_genres_data(
            connection=connection,
            genre_ids=ids,
        )
        self.logger.debug(
            "Following data was extracted from PostgreSQL: %s", genres_data
        )
        return genres_data