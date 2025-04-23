"""
Fixtures for functional tests.
"""

pytest_plugins = [
    "fixtures.api_fixtures",
    "fixtures.common_fixtures",
    "fixtures.es_fixtures",
    "fixtures.redis_fixtures",
]
