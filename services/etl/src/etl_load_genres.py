"""
ETL (Extract, Transform, Load) process for transferring data from PostgreSQL to Elasticsearch.
"""

from contextlib import closing
from datetime import datetime, timedelta, timezone
import logging
import time

import psycopg
from psycopg import ClientCursor
from psycopg.rows import dict_row
from pydantic_settings import BaseSettings

from clients.redis import RedisClient
from extract import PostgresExtractor
from load import ElasticLoader
from state.redis_storage import RedisStorage
from utils.logger import FileAndConsoleLogger


class ETLSettings(BaseSettings):
    """Configuration settings for ETL."""

    timestamptz_format: str = "%Y-%m-%d %H:%M:%S.%f %z"
    limit: int = 5
    index_name: str = "genres"
    index_schema_filepath: str = "genres_schema.json"
    min_timestamptz: str = "2020-01-01 00:00:00.000 +0200"
    timezone_hours: int = 2
    sleep_interval_sec: int = 60

    class Config:
        env_prefix = "ETL_"


def get_formated_time(
    timezone_hours: int,
    timestamptz_format: str,
) -> str:
    """Get the current time formatted according to the given timestamp format.

    Args:
        timezone_hours (int): the offset from UTC in hours for the desired timezone;
        timestamptz_format (str): the format string used to format the timestamp.

    Returns:
        str: the current time formatted as a string according to the given format.
    """
    current_time = datetime.now(timezone(timedelta(hours=timezone_hours)))
    return current_time.strftime(timestamptz_format)


logger = FileAndConsoleLogger(
    name="etl_genres",
    filepath="etl_genres.log",
    level=logging.INFO,
).get_logger()
settings = ETLSettings()
extractor = PostgresExtractor(logger=logger)
loader = ElasticLoader(
    index_name=settings.index_name,
    schema_filepath=settings.index_schema_filepath,
    logger=logger,
)
state_storage = RedisStorage(redis_adapter=RedisClient().client)

while True:
    table_name = "genre"
    state_name = "etl_genres"
    logger.info("Start ETL process for %s table", state_name)
    state = state_storage.retrieve_state(state_name)
    if state[state_name] is None:
        state_storage.save_state(
            {
                state_name: {
                    "last_process_timestamptz": settings.min_timestamptz,
                    "offset": 0,
                }
            }
        )
        state = state_storage.retrieve_state(state_name)
    state = state[state_name]

    current_timestamptz = get_formated_time(
        timezone_hours=settings.timezone_hours,
        timestamptz_format=settings.timestamptz_format,
    )
    last_process_timestamptz = state["last_process_timestamptz"]
    offset = state["offset"]

    with closing(
        psycopg.connect(
            **extractor.dsl,
            row_factory=dict_row,
            cursor_factory=ClientCursor,
        )
    ) as pg_conn:
        while True:
            batch = extractor.extract_genres(
                connection=pg_conn,
                table_name=table_name,
                start_timestamptz=last_process_timestamptz,
                stop_timestamptz=current_timestamptz,
                limit=settings.limit,
                offset=offset,
            )
            if len(batch) == 0:
                logger.info("No new data for table %s, skipping", state_name)
                break
            elastic_batch = [
                {"id": row.get("id"), "name": row.get("name")} for row in batch
            ]
            loader.load(elastic_batch)
            state_storage.save_state(
                {
                    state_name: {
                        "last_process_timestamptz": last_process_timestamptz,
                        "offset": offset,
                    }
                }
            )
            offset += settings.limit
            if len(batch) != settings.limit:
                break
        state_storage.save_state(
            {
                state_name: {
                    "last_process_timestamptz": current_timestamptz,
                    "offset": 0,
                }
            }
        )
        logger.info("ETL process for %s table finished", state_name)
    logger.info(
        "ETL process finished for all tables, sleeping %s sec",
        settings.sleep_interval_sec,
    )
    time.sleep(settings.sleep_interval_sec)
