from enum import Enum


class RetryJitterType(Enum):
    FULL = "full"
    EQUAL = "equal"
    NONE = "none"
