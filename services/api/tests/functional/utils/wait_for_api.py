"""
API connection wait script.
"""

import logging

import backoff
import requests

from settings import APISettings

settings = APISettings()


def is_api_available(url: str) -> bool:
    """Checks if the API is available.

    Args:
        url (str): API URL.

    Returns:
        bool: True if API responds to a healthcheck, False otherwise.
    """
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        return data.get("status") == "ok"
    except requests.exceptions.RequestException:
        return False


@backoff.on_predicate(
    backoff.expo,
    predicate=lambda result: not result,
    max_tries=5,
    jitter=backoff.random_jitter,
)
def wait_for_api(url: str):
    """Waits for API to become available using exponential backoff.

    Args:
        url (str): API URL.

    Raises:
        ConnectionError: if API is not available after retries.
    """
    api_available = is_api_available(url)
    if not api_available:
        logging.warning("API is not available.")
    return api_available


if __name__ == "__main__":
    wait_for_api(url=f"http://{settings.container_name}:{settings.port}/api/health")
