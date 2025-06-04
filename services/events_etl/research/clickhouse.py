import json
from typing import Type

from pydantic import BaseModel
from clickhouse_driver import Client


class ClickHouseLoader:
    def __init__(self, cluster_name: str = 'company_cluster', db_name: str = 'shard') -> None:
        self.client = Client(host='clickhouse-node-1')
        self.cluster_name = cluster_name
        self.db_name = db_name

    def insert_batch(self, table: str, fields: tuple[str], batch: list[Type[BaseModel]]) -> None:
        fields_str = f"({', '.join(fields)})"
        values = []

        for model in batch:
            dumped = model.model_dump()
            row = []
            for field in fields:
                val = dumped.get(field)
                if val is None:
                    row.append('NULL')
                elif isinstance(val, (dict, list)):
                    json_str = json.dumps(val).replace("'", "''")  # экранирование одинарных кавычек
                    row.append(f"'{json_str}'")
                elif isinstance(val, str):
                    escaped = val.replace("'", "''")  # экранировать одинарные кавычки
                    row.append(f"'{escaped}'")
                else:
                    row.append(str(val))
            values.append(f"({', '.join(row)})")

        values_str = ',\n'.join(values)
        query = f"INSERT INTO {self.db_name}.{table} {fields_str} VALUES {values_str}"
        self.client.execute(query)

    def create_tables(self, tables: list[str]) -> None:
        self._create_database()
        if 'film_frame' in tables:
            self.client.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.db_name}.film_frame_local
                ON CLUSTER company_cluster
                (
                    type String,
                    event_name String,
                    payload String,
                    timestamp Float64,
                    user_id UUID
                )
                ENGINE = MergeTree()
                ORDER BY (timestamp, user_id);
            """)

            # Distributed таблица
            self.client.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.db_name}.film_frame
                ON CLUSTER company_cluster
                AS {self.db_name}.film_frame_local
                ENGINE = Distributed({self.cluster_name}, {self.db_name}, film_frame_local, rand());
            """)

    def _create_database(self) -> None:
        self.client.execute(f'CREATE DATABASE IF NOT EXISTS {self.db_name} ON CLUSTER company_cluster')

    def read_sample(self, table: str, limit: int = 100) -> list[dict]:
        query = f"SELECT * FROM {self.db_name}.{table} LIMIT {limit}"
        rows = self.client.execute(query, with_column_types=True)
        columns = [col[0] for col in rows[1]]
        return [dict(zip(columns, row)) for row in rows[0]]