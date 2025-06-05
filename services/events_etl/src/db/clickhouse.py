import datetime
import json
from typing import Type
import uuid

from clickhouse_driver import Client
from pydantic import BaseModel

from core.config import clickhouse_settings


class ClickHouseLoader:
    def __init__(
        self,
        cluster_name: str = clickhouse_settings.cluster,
        db_name: str = clickhouse_settings.db,
    ) -> None:
        self.client = Client(host=clickhouse_settings.host)
        self.cluster_name = cluster_name
        self.db_name = db_name

    def insert_batch(
        self, table: str, fields: tuple[str], batch: list[Type[BaseModel]]
    ) -> None:
        fields_str = f"({', '.join(fields)})"
        values = []

        for model in batch:
            dumped = model.model_dump()
            row = []
            for field in fields:
                val = dumped.get(field)
                if val is None:
                    row.append("NULL")
                elif isinstance(val, (dict, list)):
                    json_str = json.dumps(val).replace(
                        "'", "''"
                    )  # экранирование одинарных кавычек
                    row.append(f"'{json_str}'")
                elif isinstance(val, datetime.datetime):
                    formatted = val.astimezone(datetime.timezone.utc).strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )[:23]
                    row.append(f"'{formatted}'")
                elif isinstance(val, uuid.UUID):
                    row.append(f"'{str(val)}'")
                elif isinstance(val, str):
                    escaped = val.replace("'", "''")
                    row.append(f"'{escaped}'")
                else:
                    row.append(str(val))
            values.append(f"({', '.join(row)})")

        values_str = ",\n".join(values)
        query = f"INSERT INTO {self.db_name}.{table} {fields_str} VALUES {values_str}"
        self.client.execute(query)

    def _create_database(self) -> None:
        self.client.execute(
            f"CREATE DATABASE IF NOT EXISTS {self.db_name} ON CLUSTER {self.cluster_name}"
        )

    def create_tables(self) -> None:
        self._create_database()
        self._create_click_events()
        self._create_custom_events()

    def _create_click_events(self) -> None:
        self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.db_name}.click_events_local
            ON CLUSTER {self.cluster_name} (
                event_id UUID,
                user_id String,
                timestamp DateTime64(3, 'UTC'),
                x Int32,
                y Int32,
                element String,
                element_id String,
                element_classes String,
                url String,
                event_type LowCardinality(String)
            )
            ENGINE = MergeTree
            PARTITION BY toYYYYMM(timestamp)
            ORDER BY (timestamp, user_id);
        """)

        self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.db_name}.click_events
            ON CLUSTER {self.cluster_name}
            AS {self.db_name}.click_events_local
            ENGINE = Distributed({self.cluster_name}, {self.db_name}, click_events_local, rand());
        """)

    def _create_custom_events(self) -> None:
        self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.db_name}.custom_events_local
            ON CLUSTER {self.cluster_name} (
                event_id UUID,
                user_id String,
                timestamp DateTime64(3, 'UTC'),
                event_type LowCardinality(String),
                film_id String DEFAULT '',
                before_quality LowCardinality(String) DEFAULT '',
                after_quality LowCardinality(String) DEFAULT '',
                stop_time Int32 DEFAULT 0,
                filter_by LowCardinality(String) DEFAULT ''
            )
            ENGINE = MergeTree
            PARTITION BY toYYYYMM(timestamp)
            ORDER BY (event_type, timestamp);
        """)

        self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.db_name}.custom_events
            ON CLUSTER {self.cluster_name}
            AS {self.db_name}.custom_events_local
            ENGINE = Distributed({self.cluster_name}, {self.db_name}, custom_events_local, rand());
        """)
