from http import HTTPStatus

from flask import Flask, jsonify, Response


app = Flask(__name__)


@app.route("/api/health")  # type: ignore[misc]
def health() -> tuple[Response, int]:
    return jsonify(status="healthy"), HTTPStatus.OK
