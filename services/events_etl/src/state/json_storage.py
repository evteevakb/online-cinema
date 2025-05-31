"""Provides implementation of ETL state storage using JSON file."""

import json
import os
from typing import Any

from state.base_storage import BaseStorage


class JsonFileStorage(BaseStorage):
    def __init__(
            self,
            filepath: str,
            ) -> None:
        self.filepath = filepath

    def save_state(self, state: dict[str, Any]) -> None:
        """Save the state to JSON file."""
        with open(self.filepath, "w") as f:
            json.dump(state, f)

    def retrieve_state(self, key: str) -> Any:
        """Retrieve the state from JSON file."""
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                state = json.load(f)
            return {key: state[key]}
        return {key: 0}
