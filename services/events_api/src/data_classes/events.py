from dataclasses import dataclass
import datetime
import uuid

UTC = datetime.timezone.utc


@dataclass
class QualityVideoChangeEvent:
    """Helps tracking video quality change."""
    event_id: str
    user_id: str
    film_id: str
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


class VideoStopEvent:
    """Helps tracking when user stoped film."""
    event_id: str
    user_id: str
    film_id: str
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


class FilterEvent:
    event_id: str
    user_id: str
    film_id: str
    filter_by: str
    event_type: str = "filter"

    @classmethod
    def create(cls, user_id: str, film_id: str, filter_by: str):
        return cls(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            film_id=film_id,
            filter_by=filter_by,
            timestamp=datetime.datetime.now(UTC).isoformat()
        )
