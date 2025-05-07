"""
Provides a decorator for adding exponential backoff with jitter to methods.
"""

import traceback
from functools import wraps
from random import uniform
from time import sleep
from typing import Callable, cast, ParamSpec, Type, TypeVar
from typing_extensions import Self


E = TypeVar("E", bound=Exception)
P = ParamSpec("P")
R = TypeVar("R")


def backoff(
    min_delay_sec: float,
    max_delay_sec: float,
    max_retries: int,
    factor: int,
    retry_exceptions: list[Type[E]],
    jitter: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def wrapper(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def inner(self: Self, *args: P.args, **kwargs: P.kwargs) -> R:
            current_delay = min_delay_sec
            retries_num = 1

            while retries_num <= max_retries + 1:
                try:
                    return func(self, *args, **kwargs)
                except Exception as exc:
                    if type(exc) in retry_exceptions:
                        if retries_num > max_retries:
                            self.logger.error(
                                "Function %s failed with exception %s: %s. Traceback:\n %s",
                                func.__name__,
                                type(exc).__name__,
                                str(exc),
                                "".join(traceback.format_tb(exc.__traceback__)),
                            )
                            raise
                        self.logger.warning(
                            "Function %s failed with exception %s: %s. Retry %s of %s with delay %s sec.",
                            func.__name__,
                            type(exc).__name__,
                            str(exc),
                            retries_num,
                            max_retries,
                            current_delay,
                        )
                        sleep(current_delay)
                        current_delay = round(
                            min(current_delay * factor, max_delay_sec), 2
                        )
                        if jitter:
                            current_delay = round(
                                min(current_delay + uniform(-1, 3), max_delay_sec), 2
                            )
                        retries_num += 1
                    else:
                        self.logger.error(
                            "Function %s failed with exception %s: %s. Traceback:\n %s",
                            func.__name__,
                            type(exc).__name__,
                            str(exc),
                            "".join(traceback.format_tb(exc.__traceback__)),
                        )
                        raise
            raise RuntimeError("Unexpected exit from retry loop")

        return cast(Callable[P, R], inner)

    return wrapper
