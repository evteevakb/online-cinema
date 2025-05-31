"""
ETL (Extract, Transform, Load) process for transferring data from Kafka to ClickHouse.
"""

from time import sleep

from core.config import etl_settings, kafka_settings
from state.json_storage import JsonFileStorage
from clients.kafka import KafkaConsumerContext
from utils.logger import Logger

logger = Logger.get_logger(name=__name__, prefix="Main loop: ")
file_storage = JsonFileStorage(filepath=etl_settings.state_storage_file)


while True:
    for topic in kafka_settings.topics_list:
        state = file_storage.retrieve_state(topic)
        with KafkaConsumerContext() as consumer:
            if not consumer:
                logger.warning("Skipping ETL due to Kafka connection failure")
    sleep(etl_settings.sleep_interval_sec)
