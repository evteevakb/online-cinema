from http import HTTPStatus

from flask import Blueprint, jsonify, request, Response

from config import kafka_settings
from data_classes.events import CLickEvent
from kafka_utils import KafkaProducerClient

click_route = Blueprint("click_route", __name__)
kafka_producer = KafkaProducerClient(
    bootstrap_servers=kafka_settings.bootstrap_servers, topic="click"
)


@click_route.route("/events/click", methods=["POST"])
def create_click_event() -> tuple[Response, HTTPStatus]:
    """Creates click event.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """

    data = request.get_json()
    user_id = data.get("user_id")
    x = data.get("x")
    y = data.get("y")
    element = data.get("element")
    element_id = data.get("element_id")
    element_classes = data.get("element_classes")
    url = data.get("url")

    try:
        event = CLickEvent(
            user_id=user_id,
            x=x,
            y=y,
            element=element,
            element_id=element_id,
            element_classes=element_classes,
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
