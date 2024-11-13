from enum import Enum
from typing import Literal


class MediaType(Enum):
    NONE = 0
    IMAGE = 1
    GIF = 2
    VIDEO = 3
    GALLERY = 4


class Feed(Enum):
    TOP = 0
    HOT = 1
    NEW = 2
    CONTROVERSIAL = 3
    RISING = 4


TimeFilter = Literal["all", "day", "hour", "month", "week", "year"]
