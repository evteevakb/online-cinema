"""
Abstract base class for OAuth providers.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """Abstract base class for OAuth providers."""

    provider_name: str

    @abstractmethod
    async def get_auth_url(self, *args: Any, **kwargs: Any) -> Any:
        """Generate the URL to initiate the OAuth authentication process.

        Returns:
            Any: A provider-specific authentication URL or redirect instruction.
        """

    @abstractmethod
    async def get_user_info(self, *args: Any, **kwargs: Any) -> Any:
        pass
