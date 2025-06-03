from http import HTTPStatus

from flask import Blueprint, jsonify, request, Response

from config import kafka_settings
from data_classes.events import DwellTime
from kafka_utils import KafkaProducerClient

dwell_route = Blueprint("dwell_route", __name__)
kafka_producer = KafkaProducerClient(
    bootstrap_servers=kafka_settings.bootstrap_servers, topic="dwell_time"
)


@dwell_route.route("/events/dwell_time", methods=["POST"])
def create_dwell_time_event() -> tuple[Response, HTTPStatus]:
    """Creates click event.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """

    data = request.get_json()
    user_id = data.get("user_id")
    dwell_time = data.get("dwell_time")
    url = data.get("url")

    try:
        event = DwellTime(
            user_id=user_id,
            dwell_time=dwell_time,
            url=url,
        ).model_dump_json()
        event_in_bytes = str.encode(event)
        with kafka_producer as producer:
            producer.send(event_in_bytes)
        return jsonify(event=event), HTTPStatus.OK
    except ValueError as err:
        return jsonify(error=str(err)), HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception as err:
        return jsonify(error=str(err)), HTTPStatus.INTERNAL_SERVER_ERROR
