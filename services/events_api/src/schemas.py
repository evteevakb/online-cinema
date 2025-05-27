from marshmallow import fields, Schema


class KafkaMessageSchema(Schema):
    topic = fields.String(required=True, validate=lambda s: len(s) > 0)
    value = fields.String(required=True, validate=lambda s: len(s) > 0)
    key = fields.String(required=False, allow_none=True, validate=lambda s: s is None or len(s) > 0)


kafka_message_schema = KafkaMessageSchema()
