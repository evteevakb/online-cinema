from http import HTTPStatus

from flask import Blueprint, jsonify, request, Response

from config import kafka_settings
from data_classes.events import FilterEvent
from kafka_utils import KafkaProducerClient

filter_route = Blueprint("filter_route", __name__)
kafka_producer = KafkaProducerClient(
    bootstrap_servers=kafka_settings.bootstrap_servers, topic="filter"
)


@filter_route.route("/events/filter", methods=["POST"])
def filter_event() -> tuple[Response, HTTPStatus]:
    """Creates video quality event.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    film_id = data.get("film_id")
    filter_by = data.get("filter_by")
    try:
        event = FilterEvent(
            user_id=user_id, film_id=film_id, filter_by=filter_by
        ).to_json()
        event_in_bytes = str.encode(event)
        kafka_producer.send(event_in_bytes)
        return jsonify(event=event), HTTPStatus.OK
    except Exception as err:
        return jsonify(error=str(err)), HTTPStatus.INTERNAL_SERVER_ERROR
