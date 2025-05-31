import logging
import sys

from core.config import etl_settings


class Logger:
    _loggers = {}
    log_level = etl_settings.log_level


    @staticmethod
    def get_logger(
        name: str,
        prefix: str,
        ) -> logging.Logger:
        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(Logger.log_level)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(f"%(asctime)s | {prefix} %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(handler)

        logger.propagate = False

        Logger._loggers[name] = logger
        return logger
