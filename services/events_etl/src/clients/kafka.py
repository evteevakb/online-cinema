"""
Kafka consumer.
"""

from types import TracebackType
from typing import Type

import backoff
from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

from core.config import kafka_settings
from utils.logger import Logger

logger = Logger.get_logger("kafka_consumer", prefix="KafkaConsumer: ")
max_retries = kafka_settings.connection_max_retries


class KafkaConsumerContext:
    """Context manager for managing a KafkaConsumer."""

    def __init__(
        self,
    ) -> None:
        self.bootstrap_servers = kafka_settings.bootstrap_servers
        self.consumer = None

    @backoff.on_exception(
        backoff.expo,
        (KafkaError, NoBrokersAvailable),
        max_tries=max_retries,
        jitter=None,
    )
    def _connect(
        self,
    ) -> KafkaConsumer:
        """Establish a connection to the Kafka broker with retries.

        Returns:
            KafkaConsumer: A configured KafkaConsumer instance.

        Raises:
            KafkaError: If a Kafka-related error occurs.
            NoBrokersAvailable: If no Kafka brokers are available.
        """
        logger.debug(f"Trying to connect to Kafka at {self.bootstrap_servers}...")
        return KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            consumer_timeout_ms=1000,
        )

    def __enter__(
        self,
    ) -> KafkaConsumer | None:
        """Enter the runtime context and open a connection to Kafka.

        Returns:
            KafkaConsumer | None: The KafkaConsumer if connected successfully, else None.
        """
        try:
            self.consumer = self._connect()
            logger.debug("Kafka was successfully connected")
            return self.consumer
        except (KafkaError, NoBrokersAvailable) as exc:
            logger.exception(f"Failed to connect after {max_retries} retries: {exc}")
            return None

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the runtime context and close connection to Kafka.

        Args:
            exc_type (Type[BaseException] | None): The exception type, if raised.
            exc_val (BaseException | None): The exception value, if raised.
            exc_tb (TracebackType | None): The traceback, if an exception was raised.
        """
        if exc_type is not None:
            logger.error(f"{exc_type}: {exc_val}. Traceback: {exc_tb}")
        if self.consumer:
            self.consumer.close()
            logger.debug("Kafka was successfully disconnected")
