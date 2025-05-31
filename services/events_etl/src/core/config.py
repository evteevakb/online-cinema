"""
Configuration settings for the events ETL service.
"""

from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class ETLSettings(BaseSettings):
    """Configuration settings for ETL process"""

    log_level: int
    sleep_interval_sec: int
    state_storage_file: str

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        allowed_levels = {0, 10, 20, 30, 40, 50}
        if v not in allowed_levels:
            raise ValidationError(f"log_level must be one of {sorted(allowed_levels)}")
        return v

    model_config = SettingsConfigDict(env_prefix="ETL_")


class KafkaSettings(BaseSettings):
    """Configuration settings for Kafka."""

    bootstrap_servers: str
    connection_max_retries: int
    topics: str

    model_config = SettingsConfigDict(env_prefix="KAFKA_")

    @property
    def topics_list(self) -> list[str]:
        return [t.strip() for t in self.topics.split(",") if t.strip()]


etl_settings = ETLSettings()
kafka_settings = KafkaSettings()
