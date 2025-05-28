"""
Contains Kafka utility classes.
"""

from types import TracebackType
from typing import Self, Type

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


class KafkaTopicManager:
    """Context-managed Kafka topic manager.

    Args:
        bootstrap_servers (str): Kafka bootstrap server(s).
    """

    def __init__(
        self,
        bootstrap_servers: str,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.admin_client: KafkaAdminClient | None = None

    def __enter__(
        self,
    ) -> Self:
        """Initializes KafkaAdminClient upon entering the context."""
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Closes KafkaAdminClient upon exiting the context."""
        if self.admin_client:
            self.admin_client.close()

    def topic_exists(
        self,
        topic_name: str,
    ) -> bool:
        """Checks if the given Kafka topic already exists.

        Args:
            topic_name (str): The name of the topic to check.

        Returns:
            bool: True if the topic exists, False otherwise.

        Raises:
            RuntimeError: If called outside of a context manager.
        """
        if not self.admin_client:
            raise RuntimeError(
                "Admin client not initialized. Use within a context manager."
            )
        existing_topics = self.admin_client.list_topics()
        return topic_name in existing_topics

    def create_topic(
        self,
        topic_name: str,
        num_partitions: int = 3,
        replication_factor: int = 3,
    ) -> None:
        """Creates a new Kafka topic if it does not already exist.

        Args:
            topic_name (str): Name of the Kafka topic to create.
            num_partitions (int): Number of partitions for the topic.
            replication_factor (int): Replication factor for the topic.

        Raises:
            RuntimeError: If called outside of a context manager.
        """
        if not self.admin_client:
            raise RuntimeError(
                "Admin client not initialized. Use within a context manager."
            )
        try:
            topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
            )
            self.admin_client.create_topics([topic])
            print(f"Topic '{topic_name}' created.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")


class KafkaProducerClient:
    """Context-managed Kafka producer for sending messages.

    Args:
        bootstrap_servers (str): Kafka bootstrap server(s).
        topic (str): Kafka topic to which messages will be sent.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: KafkaProducer | None = None

    def __enter__(
        self,
    ) -> Self:
        """Initializes KafkaProducer upon entering the context."""
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        return self

    def send(
        self,
        value: bytes,
        key: bytes | None = None,
    ) -> None:
        """Sends a message to the Kafka topic.

        Args:
            value (bytes): The message payload.
            key (bytes | None): Optional key to partition messages.

        Raises:
            RuntimeError: If called outside of a context manager.
        """
        if not self.producer:
            raise RuntimeError(
                "Producer is not initialized. Use within a context manager."
            )
        self.producer.send(self.topic, key=key, value=value)

    def flush(
        self,
    ) -> None:
        """Flushes any buffered messages."""
        if self.producer:
            self.producer.flush()

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Flushes and closes the KafkaProducer upon exiting the context."""
        if self.producer:
            self.producer.flush()
            self.producer.close()
