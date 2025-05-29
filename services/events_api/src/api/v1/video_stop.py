from http import HTTPStatus

from app import app
from flask import Response

from data_classes.events import VideoStopEvent
from kafka_utils import KafkaProducerClient, KafkaTopicManager

kafka_producer = KafkaProducerClient(
    bootstrap_servers=["localhost:9094"], topic="video_stop"
)

kafka_topic = KafkaTopicManager(bootstrap_servers=["localhost:9094"])


@app.before_first_request
def create_tables():
    kafka_topic.create_topic("video_stop")


@app.route("/api/events/video_stop", methods=["POST"])
def create_vid_stop_event(
    user_id: str, film_id: str, stop_time: str
) -> tuple[Response, HTTPStatus]:
    """Creates video quality event.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """
    event = VideoStopEvent(
        user_id=user_id, film_id=film_id, stop_time=stop_time
    ).to_json()
    event_in_bytes = str.encode(event)
    kafka_producer.send(event_in_bytes)
    return (event, HTTPStatus.OK)
