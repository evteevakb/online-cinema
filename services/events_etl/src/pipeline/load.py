from clients.kafka import KafkaConsumerContext
from core.config import etl_settings
from db.clickhouse import ClickHouseLoader
from schemas.events import (
    BaseEvent,
    CLickEvent,
    CustomEvent,
    DwellTime,
    FilterEvent,
    QualityVideoChangeEvent,
    VideoStopEvent,
)
from utils.logger import Logger

logger = Logger.get_logger("load", prefix="Load: ")
clickhouse_loader = ClickHouseLoader()

EVENT_TYPE_TO_TABLE = {
    "click": "click_events",
    "video_stop": "custom_events",
    "quality_change": "custom_events",
    "filter": "custom_events",
    "dwell_time": "custom_events",
}

CUSTOM_EVENTS_SCHEMAS = [DwellTime, QualityVideoChangeEvent, FilterEvent, DwellTime]


def load_batch_to_clickhouse(events: list[BaseEvent]) -> None:
    if not events:
        logger.info("No events to load. Skipping batch.")
        return

    batches_by_table: dict[str, list[BaseEvent]] = {}

    for event in events:
        table_name = EVENT_TYPE_TO_TABLE.get(event.event_type)
        if not table_name:
            logger.warning(f"Unknown event_type: {event.event_type}. Skipping.")
            continue
        batches_by_table.setdefault(table_name, []).append(event)

    for table, batch in batches_by_table.items():
        logger.info(f"Loading {len(batch)} events into '{table}' table.")

        if type(batch[0]) in CUSTOM_EVENTS_SCHEMAS:
            batch = [CustomEvent.from_event(e) for e in batch]
            model_fields = list(CustomEvent.model_fields.keys())
        else:
            model_fields = list(type(batch[0]).model_fields.keys())
            logger.info(f"Model fields %s", model_fields)
        clickhouse_loader.insert_batch(table=table, fields=model_fields, batch=batch)
