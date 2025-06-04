import multiprocessing
import datetime
import random
from time import time as now
import uuid
from typing import Type

from pydantic import BaseModel, Field


class TestData:
    def __init__(self, schema: Type[BaseModel], size: int = 10_000_000, batch: int = 1000, workers: int = 4):
        self.schema = schema
        self.size = size
        self.batch = batch
        self.workers = workers

    def _generate_batch(self, batch_size):
        return [self.schema() for _ in range(batch_size)]

    def _worker_wrapper(self, args):
        batch = args[0]
        return self._generate_batch(batch)

    def generate_data_multiprocessing(self):
        batch_count = self.size // self.batch
        remaining = self.size % self.batch

        with multiprocessing.Pool(processes=self.workers) as pool:
            args = [(self.batch,) for _ in range(batch_count)]
            for result in pool.imap_unordered(self._worker_wrapper, args):
                yield result

            if remaining:
                yield self._generate_batch(remaining)

    def generate_data(self):
        for _ in range(self.size // self.batch):
            batch_data = [self.schema() for _ in range(self.batch)]
            yield batch_data

        remaining = self.size % self.batch
        if remaining:
            yield [self.schema() for _ in range(remaining)]


class FilmFramePayload(BaseModel):
    movie_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    viewed_frame: int = Field(default_factory=lambda: random.randint(1, 10_000_000_000))


class FilmFrame(BaseModel):
    type: str = 'custom'
    event_name: str = 'filmFrame'
    payload: FilmFramePayload = Field(default_factory=lambda: FilmFramePayload())
    timestamp: int = int(datetime.datetime.now().timestamp())
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
