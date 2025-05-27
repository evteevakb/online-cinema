from typing import Self

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from kafka import KafkaProducer


class KafkaTopicManager:
    def __init__(
            self,
            bootstrap_servers: str,
            ) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.admin_client: KafkaAdminClient | None = None

    def __enter__(
            self,
            ) -> Self:
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.admin_client:
            self.admin_client.close()

    def topic_exists(
            self,
            topic_name: str,
            ) -> bool:
        existing_topics = self.admin_client.list_topics()
        return topic_name in existing_topics

    def create_topic(
            self, 
            topic_name: str,
            num_partitions: int = 3,
            replication_factor: int = 3,
            ) -> None:
        if not self.admin_client:
            raise RuntimeError("Admin client not initialized. Use within a context manager.")
        if self.topic_exists(topic_name=topic_name):
            return
        try:
            topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
            self.admin_client.create_topics([topic])
            print(f"Topic '{topic_name}' created.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")


class KafkaProducerClient:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: KafkaProducer | None = None

    def __enter__(self) -> Self:
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        return self

    def send(self, value: bytes, key: bytes | None = None) -> None:
        if not self.producer:
            raise RuntimeError("Producer is not initialized. Use within a context manager.")
        self.producer.send(self.topic, key=key, value=value)

    def flush(self) -> None:
        if self.producer:
            self.producer.flush()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.producer:
            self.producer.flush()
            self.producer.close()
