"""
Configuration settings for the events ETL service.
"""

from datetime import timezone

from dateutil import parser as dtparser
from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class ETLSettings(BaseSettings):
    """Configuration settings for ETL process"""

    log_level: int
    sleep_interval_sec: int
    state_storage_file: str
    batch_size: int
    min_timestamptz: str = "2020-01-01T00:00:00.000Z"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: int) -> int:
        """Validate that the log level is among accepted values.

        Args:
            v (int): The provided log level.

        Returns:
            int: Validated log level.

        Raises:
            ValidationError: If the log level is not one of the allowed values.
        """
        allowed_levels = {0, 10, 20, 30, 40, 50}
        if v not in allowed_levels:
            raise ValidationError(f"log_level must be one of {sorted(allowed_levels)}")
        return v

    @field_validator("min_timestamptz")
    @classmethod
    def validate_and_convert_timestamptz(cls, v: str) -> str:
        """Validate and normalize the timestamp with timezone to UTC ISO format.

        Args:
            v (str): A timestamp string.

        Returns:
            str: A normalized ISO 8601 timestamp in UTC with 'Z' suffix.

        Raises:
            ValueError: If the timestamp format is invalid or lacks timezone info.
        """
        try:
            dt = dtparser.parse(v)
        except Exception:
            raise ValueError(f"Invalid timestamp format: {v}")
        if not dt.tzinfo:
            raise ValueError(
                "Timestamp must include a timezone offset (e.g., 'Z' or '+02:00')"
            )
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.isoformat().replace("+00:00", "Z")

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


class ClickHouseSettings(BaseSettings):
    """Configuration settings for Kafka."""

    host: str
    cluster: str
    db: str

    model_config = SettingsConfigDict(env_prefix="CLICKHOUSE_")


etl_settings = ETLSettings()
kafka_settings = KafkaSettings()
clickhouse_settings = ClickHouseSettings()
