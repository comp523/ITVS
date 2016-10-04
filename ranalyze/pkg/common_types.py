from datetime import (date, datetime)
from praw.objects import (Comment, Submission)
from typing import (Tuple, Union)

Date = Union[date, datetime]
DateRange = Tuple[Date, Date]
IntRange = Tuple[int, int]
PrawEntry = Union[Comment, Submission]
