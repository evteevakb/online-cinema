from http import HTTPStatus

from app import app
from flask import Response

from data_classes.events import FilterEvent
from kafka_utils import KafkaProducerClient, KafkaTopicManager

kafka_producer = KafkaProducerClient(
    bootstrap_servers=["localhost:9094"], topic="filter"
)

kafka_topic = KafkaTopicManager(bootstrap_servers=["localhost:9094"])


@app.before_first_request
def create_tables():
    kafka_topic.create_topic("filter")


@app.route("/api/events/filter", methods=["POST"])
def filter_event(
    user_id: str, film_id: str, stop_time: str, filter_by: str
) -> tuple[Response, HTTPStatus]:
    """Creates video quality event.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """
    try:
        event = FilterEvent(
            user_id=user_id, film_id=film_id, filter_by=filter_by
        ).to_json()
        event_in_bytes = str.encode(event)
        kafka_producer.send(event_in_bytes)
        return (event, HTTPStatus.OK)
    except Exception as err:
        return (err, HTTPStatus.INTERNAL_SERVER_ERROR)
