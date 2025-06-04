from core.config import etl_settings
from core.kafka import KafkaConsumerContext
from etl.extract import extract_batch
from etl.transform import transform_batch
from storage.clickhouse_loader import ClickHouseLoader
from models import EventBase
from utils.logger import Logger

logger = Logger.get_logger("load", prefix="Load: ")
clickhouse_loader = ClickHouseLoader()

EVENT_TYPE_TO_TABLE = {
    "click": "click_events",
    "page_view": "page_view_events",
    "video_stop": "custom_events",
    "quality_change": "custom_events",
    "filter": "custom_events"
}

def load_batch_to_clickhouse(events: list[EventBase]) -> None:
    if not events:
        logger.info("No events to load. Skipping batch.")
        return

    batches_by_table: dict[str, list[EventBase]] = {}

    for event in events:
        table_name = EVENT_TYPE_TO_TABLE.get(event.event_type)
        if not table_name:
            logger.warning(f"Unknown event_type: {event.event_type}. Skipping.")
            continue
        batches_by_table.setdefault(table_name, []).append(event)

    for table, batch in batches_by_table.items():
        logger.info(f"Loading {len(batch)} events into '{table}' table.")
        clickhouse_loader.insert_batch(table=table, batch=batch)
