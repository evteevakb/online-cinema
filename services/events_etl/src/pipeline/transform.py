from typing import Type, Any

from pydantic import BaseModel, ValidationError
from utils.logger import Logger

from schemas.events import (
    CLickEvent,
    DwellTime,
    QualityVideoChangeEvent,
    VideoStopEvent,
    FilterEvent
)

logger = Logger.get_logger("transform", prefix="Transform: ")


def transform_batch(batch: list[Type[BaseModel]], topic: str) -> list[BaseModel]:
    """
    Validates and normalizes a batch of raw event data.

    Args:
        batch (list[BaseModel | dict]): A list of raw events (Pydantic models or dicts).
        topic (str): Kafka topic name for logging context.

    Returns:
        list[BaseModel]: A flat list of validated event instances.

    Notes:
        - Invalid or unknown events are logged and skipped.
    """
    valid_events = []

    for i, raw_event in enumerate(batch):
        try:
            event = _parse_event(raw_event)
            valid_events.append(event)
        except ValidationError as ve:
            logger.error(f"[{topic}] Validation error in event {i}: {ve}")
        except Exception as e:
            logger.error(f"[{topic}] Unexpected error in event {i}: {e}")

    return valid_events


def _parse_event(raw_event: Any) -> BaseModel:
    """
    Attempts to parse a raw event (dict or BaseModel) into a validated Pydantic model.

    Raises:
        ValueError: If the event type cannot be determined or parsed.
    """
    if isinstance(raw_event, BaseModel):
        return raw_event

    if isinstance(raw_event, dict):
        event_type = raw_event.get("event_type")

        if event_type == "click":
            return CLickEvent(**raw_event)
        elif event_type == "video_stop":
            return VideoStopEvent(**raw_event)
        elif event_type == "quality_change":
            return QualityVideoChangeEvent(**raw_event)
        elif event_type == "filter":
            return FilterEvent(**raw_event)
        elif event_type == "dwell_time":
            return DwellTime(**raw_event)

    raise ValueError(f"Unable to determine event type: {raw_event}")
