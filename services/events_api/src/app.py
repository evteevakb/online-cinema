from http import HTTPStatus

from flask import Flask, jsonify, Response
from flask_marshmallow import Marshmallow


app = Flask(__name__)
ma = Marshmallow(app)


@app.route("/api/health", methods=["GET"])  # type: ignore[misc]
def health() -> tuple[Response, int]:
    return jsonify(status="healthy"), HTTPStatus.OK
