"""create partitioning

Revision ID: b646f8f08b9b
Revises: 06e3dc0d51e9
Create Date: 2025-05-13 02:41:03.642845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import date

from db.constants import AUTH_SCHEMA

# revision identifiers, used by Alembic.
revision: str = 'b646f8f08b9b'
down_revision: Union[str, None] = '06e3dc0d51e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(f"DROP TABLE IF EXISTS {AUTH_SCHEMA}.login_history CASCADE;")
    op.execute(f"""
            CREATE TABLE {AUTH_SCHEMA}.login_history (
                uuid UUID NOT NULL,
                occurred_at TIMESTAMP NOT NULL DEFAULT now(),
                user_uuid UUID REFERENCES {AUTH_SCHEMA}.users(uuid),
                user_agent TEXT,
                event_type TEXT NOT NULL,
                PRIMARY KEY (uuid, occurred_at)
            ) PARTITION BY RANGE (occurred_at);
        """)

    def generate_year_ranges(start_year: int, num_years: int = 3):
        ranges = []
        for i in range(num_years):
            year = start_year + i
            start = date(year, 1, 1)
            end = date(year + 1, 1, 1)
            ranges.append((start.isoformat(), end.isoformat()))
        return ranges

    for start, end in generate_year_ranges(2023, 3):
        partition_name = f'login_history_{start[:4]}'
        op.execute(f'''
            CREATE TABLE IF NOT EXISTS {AUTH_SCHEMA}.{partition_name}
            PARTITION OF {AUTH_SCHEMA}.login_history
            FOR VALUES FROM ('{start}') TO ('{end}');
        ''')

def downgrade():
    for year in reversed(range(2023, 2025)):
        op.execute(f"DROP TABLE IF EXISTS {AUTH_SCHEMA}.login_history_{year};")

    op.execute(f"DROP TABLE IF EXISTS {AUTH_SCHEMA}.login_history;")
