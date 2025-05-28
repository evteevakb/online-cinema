import datetime
import json
import logging
import uuid

from dataclasses import asdict, dataclass
from enum import Enum


UTC = datetime.timezone.utc


@dataclass
class BaseClass():
    event_id: str
    user_id: str
    film_id: str

    @classmethod
    def to_json(obj) -> str:
        return json.dumps(asdict(obj))


class FilterType(Enum):
    RATING = "rating"
    GENRES = "genres"
    ACTOR = "actor"


VALUES = [i.value for i in FilterType]


@dataclass
class QualityVideoChangeEvent(BaseClass):
    """Helps tracking video quality change."""
    before_quality: str
    after_quality: str
    event_type: str = "quality_change"

    @classmethod
    def create(
        cls, user_id: str, film_id: str,
        before_quality: str, after_quality: str
    ):
        return cls(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            film_id=film_id,
            before_quality=before_quality,
            after_quality=after_quality,
            timestamp=datetime.datetime.now(UTC).isoformat()
        )


@dataclass
class VideoStopEvent(BaseClass):
    """Helps tracking when user stoped film."""
    stop_time: int
    event_type: str = "video_stop"

    @classmethod
    def create(cls, user_id: str, film_id: str, stop_time: int):
        return cls(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            film_id=film_id,
            stop_time=stop_time,
            timestamp=datetime.datetime.now(UTC).isoformat()
        )


@dataclass
class FilterEvent(BaseClass):
    filter_by: str
    event_type: str = "filter"

    @classmethod
    def create(cls, user_id: str, film_id: str, filter_by: FilterType.value):
        try:
            if filter_by not in VALUES:
                raise ValueError("filter_by should be one of values: ", VALUES)
            return cls(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                film_id=film_id,
                filter_by=filter_by,
                timestamp=datetime.datetime.now(UTC).isoformat()
            )
        except ValueError as err:
            logging.error(err)
            return ""
