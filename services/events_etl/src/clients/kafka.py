
import backoff
from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

from core.config import kafka_settings
from utils.logger import Logger


logger = Logger.get_logger("kafka_consumer", prefix="KafkaConsumer: ")
max_retries = kafka_settings.connection_max_retries



class KafkaConsumerContext:
    def __init__(self, **consumer_kwargs):
        self.topics = kafka_settings.topics
        self.bootstrap_servers = kafka_settings.bootstrap_servers
        self.consumer_kwargs = consumer_kwargs
        self.consumer = None

    @backoff.on_exception(
        backoff.expo,
        (KafkaError, NoBrokersAvailable),
        max_tries=max_retries,
        jitter=None,
    )
    def _connect(self):
        logger.debug(f"Trying to connect to Kafka at {self.bootstrap_servers}...")
        return KafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            consumer_timeout_ms=1000,
            **self.consumer_kwargs,
        )

    def __enter__(self) -> KafkaConsumer | None:
        try:
            self.consumer = self._connect()
            return self.consumer
        except (KafkaError, NoBrokersAvailable) as exc:
            logger.exception(f"Failed to connect after {max_retries} retries: {exc}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.consumer:
            self.consumer.close()
