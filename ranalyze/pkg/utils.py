"""
Common utilities
"""

from typing import Union
import datetime


EPOCH = datetime.datetime.utcfromtimestamp(0)


def date_to_timestamp(date: Union[datetime.datetime, datetime.date]) -> float:
    """
    convert datetime.date object to Unix timestamp
    """
    return (date - EPOCH).total_seconds() * 1000.0
