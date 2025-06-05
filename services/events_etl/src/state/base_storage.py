"""Defines an abstract base class for storing and retrieving ETL state."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStorage(ABC):
    """Abstract state storage. Allows saving and retrieving state."""

    @abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save the state to the storage."""

    @abstractmethod
    def retrieve_state(self, key: str) -> Any:
        """Retrieve the state from the storage."""
