"""
ETL (Extract, Transform, Load) process for transferring data from Kafka to ClickHouse.
"""

from datetime import datetime, timedelta, timezone
from time import sleep

from core.config import etl_settings, kafka_settings
from state.json_storage import JsonFileStorage
from clients.kafka import KafkaConsumerContext
from pipeline.extract import extract_batch
from utils.logger import Logger

logger = Logger.get_logger(name=__name__, prefix="Main loop: ")
file_storage = JsonFileStorage(filepath=etl_settings.state_storage_file)


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
    dtparser.parse(current_time).astimezone(timezone.utc)
    return current_time.strftime(timestamptz_format)



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
        last_timestamptz = state[topic]
        current_timestamptz = get_formated_time(
            timezone_hours=etl_settings.timezone_hours,
            timestamptz_format=etl_settings.timestamptz_format,
        )

        print(last_timestamptz)
        print(current_timestamptz)

        with KafkaConsumerContext(topic_name=topic) as consumer:
            if not consumer:
                logger.warning("Skipping ETL due to Kafka connection failure")

            while True:
                batch = extract_batch(
                    consumer=consumer,
                    topic=topic,
                    start_timestamptz=last_timestamptz,
                    stop_timestamptz=current_timestamptz,
                    batch_size=etl_settings.batch_size,
                    # connection=pg_conn,
                    # table_name=table_name,
                    # start_timestamptz=last_process_timestamptz,
                    # stop_timestamptz=current_timestamptz,
                    # limit=settings.limit,
                    # offset=offset,
                )
                if len(batch) == 0:
                    logger.info("No new data for topic %s, skipping", topic)
                    break

                # TODO: transform
                # TODO: load

            #     state_storage.save_state(
            #         {
            #             table_name: {
            #                 "last_process_timestamptz": last_process_timestamptz,
            #                 "offset": offset,
            #             }
            #         }
            #     )
            #     offset += settings.limit
            #     if len(batch) != settings.limit:
            #         break
            # state_storage.save_state(
            #     {
            #         table_name: {
            #             "last_process_timestamptz": current_timestamptz,
            #             "offset": 0,
            #         }
            #     }
            # )
            logger.info("ETL process for %s topic finished", topic)

    logger.info(
        "ETL process finished for all tables, sleeping %s sec",
        etl_settings.sleep_interval_sec,
        )
    sleep(etl_settings.sleep_interval_sec)
