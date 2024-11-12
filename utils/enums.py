from enum import Enum


class MediaType(Enum):
    NONE = 0
    IMAGE = 1
    GIF = 2
    VIDEO = 3
    GALLERY = 4


class TimeFilter(Enum):
    ALL = "all"
    DAY = "day"
    HOUR = "hour"
    MONTH = "month"
    WEEK = "week"
    YEAR = "year"
