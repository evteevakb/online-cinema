from http import HTTPStatus

from app import app
from flask import Response
from kafka_utils import KafkaProducerClient, KafkaTopicManager

from data_classes.events import QualityVideoChangeEvent

kafka_producer = KafkaProducerClient(
    bootstrap_servers=['localhost:9094'], topic="video_quality"
)

kafka_topic = KafkaTopicManager(bootstrap_servers=['localhost:9094'])


@app.before_first_request
def create_tables():
    kafka_topic.create_topic("video_quality")


@app.route("/api/events/video_quality", methods=["POST"])
def create_vid_quality_event(user_id: str, film_id: str, before_quality: str, after_quality: str) -> tuple[Response, HTTPStatus]:
    """Creates video quality event.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """
    event = QualityVideoChangeEvent(
        user_id=user_id,
        film_id=film_id,
        before_quality=before_quality,
        after_quality=after_quality
    ).to_json()
    event_in_bytes = str.encode(event)
    kafka_producer.send(event_in_bytes)
    return (event, HTTPStatus.OK)
