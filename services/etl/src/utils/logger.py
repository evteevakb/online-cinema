"""
Provides a logging system with support for console and file logging.
"""

from abc import ABC, abstractmethod
import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Dict


class Logger(ABC):
    """Abstract base class for creating and managing loggers."""

    _loggers: Dict[str, logging.Logger] = {}

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        self.name = name
        self.level = level
        self.formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%d.%m.%Y %H:%M:%S",
        )

    @abstractmethod
    def _configure_logger(self) -> None:
        """Abstract method to configure the logger."""

    @abstractmethod
    def get_logger(self) -> logging.Logger:
        """Returns a configured logger instance.

        Returns:
            A configured logging.Logger instance.
        """
        if self.name in self._loggers:
            return self._loggers[self.name]
        else:
            self.logger = logging.getLogger(self.name)
            self.logger.setLevel(self.level)
            self._configure_logger()
            self._loggers[self.name] = self.logger
            return self.logger


class ConsoleLogger(Logger):
    """A logger that outputs messages to the console."""

    def _configure_logger(self) -> None:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return super().get_logger()


class FileAndConsoleLogger(ConsoleLogger):
    """A logger that outputs messages to both the console and a file."""

    def __init__(self, name: str, filepath: str, level: int = logging.INFO) -> None:
        super().__init__(name=name, level=level)
        self.filepath = filepath

    def _configure_logger(self) -> None:
        super()._configure_logger()
        file_handler = RotatingFileHandler(
            self.filepath,
            mode="a",
            maxBytes=5 * 1024 * 1024,
            backupCount=2,
        )
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        logger = super().get_logger()
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                if handler.baseFilename != os.path.abspath(self.filepath):
                    raise ValueError(
                        f"A logger with name '{self.name}' already exists, saving to {handler.baseFilename}. Please use this path."
                    )
        return logger
