"""
Fixtures for functional tests.
"""

pytest_plugins = [
    "fixtures.api_fixtures",
    "fixtures.common_fixtures",
    "fixtures.pg_fixtures",
    "fixtures.redis_fixtures",
]
