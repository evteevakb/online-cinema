"""Manages ETL state."""

from typing import Any

from state.base_storage import BaseStorage


class State:
    """A class for managing states."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Set the state for a specific key."""
        self.storage.save_state(state={key: value})

    def get_state(self, key: str) -> Any:
        """Retrieve the state for a specific key."""
        return self.storage.retrieve_state(key)
