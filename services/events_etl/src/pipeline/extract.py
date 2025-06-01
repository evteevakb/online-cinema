"""
Module for extracting batches of messages from Kafka.
"""

from datetime import datetime, timezone
import json
from typing import Any, Generator

from dateutil import parser as dtparser
from kafka import KafkaConsumer, TopicPartition

from utils.logger import Logger

logger = Logger.get_logger("extract", prefix="Extract: ")


def extract_batch(
    consumer: KafkaConsumer,
    topic: str,
    start_timestamptz: datetime,
    stop_timestamptz: datetime,
    batch_size: int,
) -> Generator[list[dict[str, Any]], None, None] | None:
    """Extracts messages from a Kafka topic within a specified time range and yields them in batches.

    Args:
        consumer (KafkaConsumer): An active KafkaConsumer instance.
        topic (str): Kafka topic to consume messages from.
        start_timestamptz (datetime): Start timestamp (inclusive) in UTC.
        stop_timestamptz (datetime): Stop timestamp (exclusive) in UTC.
        batch_size (int): Number of messages per batch.

    Returns:
        Generator[list[dict], None, None] | None: A generator yielding batches of messages as dictionaries.
                                                     Returns None if the topic has no partitions.
    """
    partitions = consumer.partitions_for_topic(topic)
    if partitions is None:
        logger.warning(f"Skipping topic {topic}: no partitions")
        return None

    topic_partitions = [TopicPartition(topic, p) for p in partitions]
    consumer.assign(topic_partitions)

    start_offsets = consumer.offsets_for_times(
        {tp: int(start_timestamptz.timestamp() * 1000) for tp in topic_partitions}
    )

    for tp in topic_partitions:
        offset_and_ts = start_offsets.get(tp)
        if offset_and_ts is not None:
            if offset_and_ts.offset is not None:
                consumer.seek(tp, offset_and_ts.offset)
            else:
                consumer.seek_to_end(tp)
        else:
            consumer.seek_to_end(tp)

    current_batch: list[dict[str, Any]] = []

    while True:
        raw_msgs = consumer.poll(timeout_ms=500)
        if not raw_msgs:
            break

        for tp, msgs in raw_msgs.items():
            for msg in msgs:
                try:
                    data = json.loads(msg.value)
                    msg_ts = dtparser.parse(data.get("timestamp")).astimezone(
                        timezone.utc
                    )
                except Exception as exc:
                    logger.exception(f"Failed to parse message {msg}: {exc}")
                    continue

                if msg_ts < start_timestamptz:
                    continue
                if msg_ts > stop_timestamptz:
                    if current_batch:
                        yield current_batch
                    break

                current_batch.append(data)
                if len(current_batch) >= batch_size:
                    yield current_batch
                    current_batch = []

    if current_batch:
        yield current_batch
    return None
