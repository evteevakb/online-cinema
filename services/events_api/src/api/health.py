from http import HTTPStatus

from flask import Blueprint, jsonify, Response

health_route = Blueprint("health_route", __name__)


@health_route.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """Health check endpoint.

    Returns:
        tuple: A tuple containing a JSON response with status.
    """
    return jsonify(status="healthy"), HTTPStatus.OK
