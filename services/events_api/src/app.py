"""
Flask application for events collection.
"""

from flask import Flask
from flask_marshmallow import Marshmallow

from api.health import health_route
from api.v1.filter import filter_route
from api.v1.quality import quality_route
from api.v1.video_stop import video_stop_route
from config import kafka_settings
from kafka_utils import KafkaTopicManager

with KafkaTopicManager(
    bootstrap_servers=kafka_settings.bootstrap_servers
) as kafka_topic:
    kafka_topic.create_topic(
        topic_name="filter",
        replication_factor=kafka_settings.topic_replication_factor,
        num_partitions=kafka_settings.topic_num_partitions,
    )
    kafka_topic.create_topic(
        topic_name="video_quality",
        replication_factor=kafka_settings.topic_replication_factor,
        num_partitions=kafka_settings.topic_num_partitions,
    )
    kafka_topic.create_topic(
        topic_name="video_stop",
        replication_factor=kafka_settings.topic_replication_factor,
        num_partitions=kafka_settings.topic_num_partitions,
    )

app = Flask(__name__)
ma = Marshmallow(app)

app.register_blueprint(health_route, url_prefix="/api")
app.register_blueprint(filter_route, url_prefix="/api/v1")
app.register_blueprint(quality_route, url_prefix="/api/v1")
app.register_blueprint(video_stop_route, url_prefix="/api/v1")
