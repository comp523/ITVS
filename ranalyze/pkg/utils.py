"""
Common utilities
"""

from datetime import datetime
from .types import Date


EPOCH = datetime.utcfromtimestamp(0)


def date_to_timestamp(date: Date) -> float:
    """
    convert datetime.datetime or datetime.date object to Unix timestamp
    """
    return (date - EPOCH).total_seconds() * 1000.0
