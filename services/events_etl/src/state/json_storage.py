"""Provides implementation of ETL state storage using JSON file."""

import json
import os
from typing import Any

from state.base_storage import BaseStorage


class JsonFileStorage(BaseStorage):
    """Stores and retrieves ETL state using a JSON file."""

    def __init__(
        self,
        filepath: str,
    ) -> None:
        self.filepath = filepath

    def save_state(self, state: dict[str, Any]) -> None:
        """Save or update the state dictionary in the JSON file.

        Args:
            state (dict[str, Any]): Dictionary containing state to save.
        """
        current_state = {}

        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                try:
                    current_state = json.load(f)
                except json.JSONDecodeError:
                    pass

        current_state.update(state)

        with open(self.filepath, "w") as f:
            json.dump(current_state, f)

    def retrieve_state(self, key: str) -> Any:
        """Retrieve a specific state value from the JSON file.

        Args:
            key (str): The key whose state value is to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the key and its value,
                or {key: None} if the key is not found or file is empty/missing.
        """
        if os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0:
            with open(self.filepath, "r") as f:
                state = json.load(f)
            if key in state:
                return {key: state[key]}
        return {key: None}
