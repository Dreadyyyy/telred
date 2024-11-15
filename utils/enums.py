from enum import Enum
from typing import Literal


class MediaType(Enum):
    NONE = 0
    IMAGE = 1
    GIF = 2
    VIDEO = 3
    GALLERY = 4
    LINK = 5


TimeFilter = Literal["all", "day", "hour", "month", "week", "year"]


FeedType = Literal["top", "hot", "new", "controversial", "rising"]
