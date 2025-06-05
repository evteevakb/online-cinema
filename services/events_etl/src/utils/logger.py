"""
Logger utility that provides prefixed loggers for ETL components.
"""

import logging
import sys

from core.config import etl_settings


class Logger:
    """Utility class for creating prefixed loggers."""

    _loggers: dict[str, logging.Logger] = {}
    log_level = etl_settings.log_level

    @staticmethod
    def get_logger(
        name: str,
        prefix: str,
    ) -> logging.Logger:
        """Get a logger instance with a specific name and prefix.

        If a logger with the given name already exists, it returns the cached
        instance. Otherwise, it creates a new logger with the specified prefix.

        Args:
            name (str): Unique name of the logger.
            prefix (str): Prefix string to include in all log messages.

        Returns:
            logging.Logger: Configured logger instance.
        """
        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(Logger.log_level)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            f"%(asctime)s | {prefix} %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(handler)

        logger.propagate = False

        Logger._loggers[name] = logger
        return logger
