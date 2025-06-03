from http import HTTPStatus

from flask import Blueprint, jsonify, request, Response

from config import kafka_settings
from data_classes.events import QualityVideoChangeEvent
from kafka_utils import KafkaProducerClient

quality_route = Blueprint("quality_route", __name__)
kafka_producer = KafkaProducerClient(
    bootstrap_servers=kafka_settings.bootstrap_servers, topic="video_quality"
)


@quality_route.route("/events/video_quality", methods=["POST"])
def create_vid_quality_event() -> tuple[Response, HTTPStatus]:
    """Creates video quality event.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    film_id = data.get("film_id")
    before_quality = data.get("before_quality")
    after_quality = data.get("after_quality")

    try:
        event = QualityVideoChangeEvent(
            user_id=user_id,
            film_id=film_id,
            before_quality=before_quality,
            after_quality=after_quality,
        ).model_dump_json()
        event_in_bytes = str.encode(event)
        with kafka_producer as producer:
            producer.send(event_in_bytes)
        return jsonify(event=event), HTTPStatus.OK
    except ValueError as err:
        return jsonify(error=str(err)), HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception as err:
        return jsonify(error=str(err)), HTTPStatus.INTERNAL_SERVER_ERROR
