"""
Common utilities
"""

from .common_types import Date
from datetime import datetime
from math import floor

EPOCH = datetime.utcfromtimestamp(0)


def date_to_timestamp(date: Date) -> int:
    """
    convert datetime.datetime or datetime.date object to Unix timestamp
    """
    return floor((date - EPOCH).total_seconds())
