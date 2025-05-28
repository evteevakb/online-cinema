"""
Configuration settings for the events service.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    """Configuration settings for Kafka."""

    bootstrap_servers: str
    topic_name: str
    topic_num_partitions: int
    topic_replication_factor: int

    model_config = SettingsConfigDict(env_prefix="KAFKA_")


kafka_settings = KafkaSettings()
