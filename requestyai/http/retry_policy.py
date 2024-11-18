import random
from typing import Iterable

import httpx

from .retry_jitter_type import RetryJitterType


class RetryPolicy:
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_BACKOFF_FACTOR: float = 0.3
    DEFAULT_STATUS_FORCELIST: dict[int, str] = {
        408: "Request timeout",
        425: "Too early",
        429: "Too many requests",
        500: "Internal server error",
        502: "Bad gateway",
        503: "Service unavailable",
        504: "Gateway timeout",
    }
    DEFAULT_ALLOWED_METHODS: set[str] = {"GET", "PUT", "DELETE"}
    DEFAULT_JITTER_TYPE = RetryJitterType.FULL

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        status_forcelist: Iterable[int] = DEFAULT_STATUS_FORCELIST.keys(),
        allowed_methods: Iterable[str] = DEFAULT_ALLOWED_METHODS,
        jitter_type: RetryJitterType = DEFAULT_JITTER_TYPE,
    ):
        self.__max_retries = max_retries
        self.__status_forcelist = set(status_forcelist)
        self.__backoff_factor = backoff_factor
        self.__allowed_methods = set(allowed_methods)
        self.__jitter_type = jitter_type

    @property
    def max_retries(self):
        return self.__max_retries

    @property
    def backoff_factor(self) -> float:
        return self.__backoff_factor

    @property
    def status_forcelist(self) -> set[int]:
        return self.__status_forcelist

    @property
    def allowed_methods(self) -> set[str]:
        return self.__allowed_methods

    @property
    def jitter_type(self) -> RetryJitterType:
        return self.__jitter_type

    def get_backoff_time(self, retry_count: int) -> float:
        """Calculate backoff delay with jitter."""

        base_delay = self.__backoff_factor * (2 ** (retry_count - 1))

        if self.__jitter_type == RetryJitterType.EQUAL:
            return base_delay / 2 + random.uniform(0, base_delay / 2)
        elif self.__jitter_type == RetryJitterType.FULL:
            return random.uniform(0, base_delay)
        else:  # RetruJitterType.NONE or any other value
            return base_delay

    def is_retry(self, response: httpx.Response, method: str) -> bool:
        """Determine if the request should be retried."""

        return (
            method.upper() in self.__allowed_methods
            and response.status_code in self.__status_forcelist
        )
