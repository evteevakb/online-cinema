"""Provides implementation of ETL state storage, using Redis."""

from contextlib import suppress
import json
from typing import Any, Dict

import redis
from state.base_storage import BaseStorage


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: redis.Redis) -> None:
        self.redis_adapter = redis_adapter

    def save_state(self, state: Dict[str, Any]) -> None:
        """Save the state to Redis."""
        for key, value in state.items():
            if isinstance(value, dict):
                value = json.dumps(value)
            self.redis_adapter.set(key, value)

    def retrieve_state(self, key: str) -> Any:
        """Retrieve the state from Redis."""
        value = self.redis_adapter.get(key)
        with suppress(TypeError):
            value = json.loads(value)
        return {key: value}
