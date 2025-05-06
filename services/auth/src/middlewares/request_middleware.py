"""
Middlewares for incoming HTTP requests.
"""

from contextvars import ContextVar
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="unknown")


def get_request_id() -> str:
    """Retrieve the request ID from the current context.

    Returns:
        str: The request ID associated with the current request.
    """
    return request_id_ctx_var.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce the presence of 'X-Request-Id' header."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process the incoming request to ensure it has an X-Request-Id.

        Args:
            request (Request): The incoming HTTP request.
            call_next (RequestResponseEndpoint): Function to proceed to the next middleware or route handler.

        Returns:
            Response: The response returned by the route handler or next middleware.
        """
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        request_id_ctx_var.set(request_id)
        return await call_next(request)
