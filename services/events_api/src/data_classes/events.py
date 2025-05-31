import datetime
from enum import Enum
import logging
from typing import Any
import uuid

from pydantic import BaseModel, Field, field_validator

UTC = datetime.timezone.utc


class FilterType(Enum):
    RATING = "rating"
    GENRES = "genres"
    ACTOR = "actor"


class QualityType(Enum):
    LOW = "360p"
    MID = "720p"
    HIGH = "1080p"


class BaseEvent(BaseModel):
    """Base class for all events"""

    user_id: str
    film_id: str
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(UTC)
    )

    @field_validator("event_id", mode="before")
    def convert_string_to_uuid(cls: Any, value: str) -> uuid.UUID:
        """Convert string UUID to UUID object if needed"""
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError as err:
                logging.error(err)
                raise ValueError("Invalid UUID format")
        return value


class QualityVideoChangeEvent(BaseEvent):
    """Helps tracking video quality change."""

    before_quality: QualityType
    after_quality: QualityType
    event_type: str = "quality_change"

    @field_validator("before_quality", "after_quality", mode="before")
    def validate_quality(cls: Any, value: QualityType) -> QualityType | str:
        """Validate quality values against enum"""
        if isinstance(value, QualityType):
            return value

        try:
            return QualityType(value)
        except ValueError as err:
            valid_values = [e.value for e in QualityType]
            logging.error(err)
            raise ValueError(
                f"Invalid quality value. "
                f"Allowed values: {', '.join(valid_values)}"
            )


class VideoStopEvent(BaseEvent):
    """Helps tracking when user stopped film."""

    stop_time: int
    event_type: str = "video_stop"

    @field_validator("stop_time")
    def validate_stop_time(cls: Any, value: int) -> int:
        """Validate stop time is non-negative"""
        if value < 0:
            raise ValueError("Stop time cannot be negative")
        return value


class FilterEvent(BaseEvent):
    """Tracks filter usage events"""

    filter_by: FilterType
    event_type: str = "filter"

    @field_validator("filter_by", mode="before")
    def validate_filter_type(cls: Any, value: FilterType) -> FilterType | str:
        """Validate filter values against enum"""
        if isinstance(value, FilterType):
            return value
        try:
            return FilterType(value)
        except ValueError as err:
            valid_values = [e.value for e in FilterType]
            logging.error(err)
            raise ValueError(
                f"Invalid filter value. "
                f"Allowed values: {', '.join(valid_values)}"
            )
