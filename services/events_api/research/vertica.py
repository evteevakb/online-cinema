import json
import os
from typing import Type
from pydantic import BaseModel
import vertica_python
from pydantic_settings import BaseSettings


class VerticaSettings(BaseSettings):
    host: str = 'vertica-node'
    port: int = 5433
    user: str = 'dbadmin'
    password: str = ''
    database: str = 'docker'
    autocommit: bool = True

    class Config:
        env_prefix = "VERTICA_"


vertica_settings = VerticaSettings()

class VerticaLoader:
    def __init__(self):
        self.connection = vertica_python.connect(**vertica_settings.model_dump())

    def insert_batch(self, table: str, fields: tuple[str], batch: list[Type[BaseModel]]):
        cursor = self.connection.cursor()
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
                    json_str = json.dumps(val).replace("'", "''")
                    row.append(f"'{json_str}'")
                else:
                    row.append(str(val))
            values.append(row)


        cursor.executemany(
            f"INSERT INTO {table} {fields_str} VALUES (%s, %s, %s, %s, %s)",
            values
        )
        cursor.close()

    def create_tables(self, tables: list[str]):
        cursor = self.connection.cursor()
        if 'film_frame' in tables:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS film_frame (
                    type VARCHAR(50),
                    event_name VARCHAR(50),
                    payload LONG VARCHAR,
                    timestamp DOUBLE PRECISION,
                    user_id UUID
                );
            """)
        cursor.close()

    def read_sample(self, table: str, limit: int = 100) -> list[dict]:
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table} LIMIT {limit}")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]