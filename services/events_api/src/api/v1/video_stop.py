from http import HTTPStatus

from flask import Blueprint, jsonify, request, Response

from config import kafka_settings
from data_classes.events import VideoStopEvent
from kafka_utils import KafkaProducerClient

video_stop_route = Blueprint("video_stop_route", __name__)
kafka_producer = KafkaProducerClient(
    bootstrap_servers=kafka_settings.bootstrap_servers, topic="video_stop"
)


@video_stop_route.route("/events/video_stop", methods=["POST"])
def create_vid_stop_event() -> tuple[Response, HTTPStatus]:
    """Creates video quality event.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    film_id = data.get("film_id")
    stop_time = data.get("stop_time")

    try:
        event = VideoStopEvent(
            user_id=user_id, film_id=film_id, stop_time=stop_time
        ).model_dump_json()
        event_in_bytes = str.encode(event)
        with kafka_producer as producer:
            producer.send(event_in_bytes)
        return jsonify(event=event), HTTPStatus.OK
    except ValueError as err:
        return jsonify(error=str(err)), HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception as err:
        return jsonify(error=str(err)), HTTPStatus.INTERNAL_SERVER_ERROR
