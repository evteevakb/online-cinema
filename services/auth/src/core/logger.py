"""
Logging configuration for the auth service.
"""

from logging import LogRecord
from typing import Any

from uvicorn.logging import AccessFormatter

from middlewares.request_middleware import get_request_id

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = [
    "console",
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": LOG_FORMAT},
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s %(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "core.logger.CustomAccessFormatter",
            "fmt": "%(asctime)s %(levelprefix)s [%(request_id)s] %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": LOG_DEFAULT_HANDLERS,
            "level": "INFO",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}


class CustomAccessFormatter(AccessFormatter):
    def formatMessage(self, record: LogRecord) -> Any:
        """Injects the request ID into the log record before formatting the access log message.

        Args:
            record (LogRecord): The log record generated for an HTTP request.

        Returns:
            Any: The formatted log message including the request ID.
        """
        request_id = get_request_id() or "unknown"
        record.request_id = request_id
        return super().formatMessage(record)
