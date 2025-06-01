"""
ETL (Extract, Transform, Load) process for transferring data from Kafka to ClickHouse.
"""

from datetime import datetime, timezone
from time import sleep

from dateutil import parser as dtparser

from clients.kafka import KafkaConsumerContext
from core.config import etl_settings, kafka_settings
from pipeline.extract import extract_batch
from state.json_storage import JsonFileStorage
from utils.logger import Logger

logger = Logger.get_logger(name=__name__, prefix="Main loop: ")
file_storage = JsonFileStorage(filepath=etl_settings.state_storage_file)


def format_time(
    timestamptz: str,
) -> datetime:
    return dtparser.parse(timestamptz).astimezone(timezone.utc)


while True:
    for topic in kafka_settings.topics_list:
        state = file_storage.retrieve_state(topic)
        if state[topic] is None:
            file_storage.save_state(
                {
                    topic: etl_settings.min_timestamptz,
                }
            )
            state = file_storage.retrieve_state(topic)
        last_timestamptz = format_time(timestamptz=state[topic])
        current_timestamptz = format_time(
            timestamptz=datetime.now(timezone.utc).isoformat()
        )

        logger.info(
            f"Start ETL pipeline for {topic=} from {last_timestamptz} to {current_timestamptz}"
        )

        with KafkaConsumerContext() as consumer:
            if not consumer:
                logger.error("Skipping ETL due to Kafka connection failure")
            else:
                for batch in extract_batch(
                    consumer=consumer,
                    topic=topic,
                    start_timestamptz=last_timestamptz,
                    stop_timestamptz=current_timestamptz,
                    batch_size=etl_settings.batch_size,
                ):
                    logger.info("Received batch with %s messages", len(batch))

                    # TODO: transform
                    # TODO: load

        file_storage.save_state(
            {
                topic: str(current_timestamptz),
            }
        )
        logger.info("ETL process for %s topic finished", topic)

    logger.info(
        "ETL process finished for all tables, sleeping %s sec",
        etl_settings.sleep_interval_sec,
    )
    sleep(etl_settings.sleep_interval_sec)
