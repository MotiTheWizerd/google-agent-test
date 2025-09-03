"""Retry utility for the memory module."""

import time
from typing import Callable, Type, Tuple


def with_retry(fn: Callable, *, retries: int = 3, backoff: float = 0.5,
               retry_on: Tuple[Type[BaseException], ...] = (Exception,)):
    """Execute a function with retries and exponential backoff."""
    for i in range(retries + 1):
        try:
            return fn()
        except retry_on as e:
            if i == retries:
                raise
            time.sleep(backoff * (2 ** i))