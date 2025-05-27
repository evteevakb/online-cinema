from http import HTTPStatus

from flask import Flask, jsonify, request, Response
from flask_marshmallow import Marshmallow
from kafka.errors import KafkaError
from marshmallow import ValidationError

from schemas import kafka_message_schema
from kafka_utils import KafkaTopicManager, KafkaProducerClient


app = Flask(__name__)
ma = Marshmallow(app)

BOOTSTRAP_SERVERS = "kafka-0:9092,kafka-1:9092,kafka-2:9092"


@app.route("/api/health", methods=["GET"])  # type: ignore[misc]
def health() -> tuple[Response, int]:
    return jsonify(status="healthy"), HTTPStatus.OK


@app.route("/api/v1/kafka/publish", methods=["POST"])
def publish_message():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), HTTPStatus.BAD_REQUEST

    try:
        data = kafka_message_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), HTTPStatus.UNPROCESSABLE_CONTENT

    app.logger.warning(f"INPUT DATA: {data}")
    try:
        with KafkaTopicManager(bootstrap_servers=BOOTSTRAP_SERVERS) as manager:
            if not manager.topic_exists(topic_name=data["topic"]):
                manager.create_topic(topic_name=data["topic"])

        with KafkaProducerClient(BOOTSTRAP_SERVERS, data["topic"]) as producer:
            key = data.get("key")
            producer.send(value=data["value"].encode(), key=key.encode() if key else None)
        return jsonify({"status": "Message sent successfully."}), 200

    except KafkaError as e:
        # TODO: handle NoBrokersAvailable
        return jsonify({"error": f"Kafka error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
