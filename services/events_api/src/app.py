"""
Flask application for events collection.
"""

from http import HTTPStatus

from flask import Flask, jsonify, request, Response
from flask_marshmallow import Marshmallow
from kafka.errors import KafkaError
from marshmallow import ValidationError

from config import kafka_settings
from kafka_utils import KafkaProducerClient, KafkaTopicManager
from schemas import kafka_message_schema

app = Flask(__name__)
ma = Marshmallow(app)


@app.route("/api/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """Health check endpoint.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """
    return jsonify(status="healthy"), HTTPStatus.OK


@app.route("/api/v1/kafka/publish", methods=["POST"])
def publish_message() -> tuple[Response, int]:
    """Publishes a validated JSON message to a Kafka topic.

    Returns:
        tuple: JSON response indicating success or failure, along with the corresponding HTTP status code.

    Raises:
        ValidationError: If the input JSON fails schema validation.
        KafkaError: If an error occurs during Kafka communication.
        Exception: For unexpected internal errors.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), HTTPStatus.BAD_REQUEST

    try:
        data = kafka_message_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), HTTPStatus.UNPROCESSABLE_CONTENT

    try:
        with KafkaTopicManager(
            bootstrap_servers=kafka_settings.bootstrap_servers
        ) as manager:
            if not manager.topic_exists(topic_name=kafka_settings.topic_name):
                manager.create_topic(
                    topic_name=kafka_settings.topic_name,
                    num_partitions=kafka_settings.topic_num_partitions,
                    replication_factor=kafka_settings.topic_replication_factor,
                )

        with KafkaProducerClient(
            bootstrap_servers=kafka_settings.bootstrap_servers,
            topic=kafka_settings.topic_name,
        ) as producer:
            key = data.get("key")
            producer.send(
                value=data["value"].encode(), key=key.encode() if key else None
            )
        return jsonify({"status": "Message sent successfully."}), HTTPStatus.OK

    except KafkaError as e:
        # TODO: handle NoBrokersAvailable
        return jsonify(
            {"error": f"Kafka error: {str(e)}"}
        ), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        return jsonify(
            {"error": f"Unexpected error: {str(e)}"}
        ), HTTPStatus.INTERNAL_SERVER_ERROR
