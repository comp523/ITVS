"""
Common utilities
"""

import datetime
from math import floor
from .constants import CHAR_SET

EPOCH = datetime.datetime.utcfromtimestamp(0)


def date_to_timestamp(date):
    """
    convert datetime.datetime or datetime.date object to Unix timestamp
    """
    if isinstance(date, datetime.date):
        date = datetime.datetime.combine(date, datetime.time.min)
    return floor((date - EPOCH).total_seconds())


def iso_to_date(iso):
    """
    Convert ISO formatted date string to datetime.date object
    """
    return datetime.datetime.strptime(iso, "%Y-%m-%d").date()


def sanitize(string):
    """

    :param string:
    :type string: str
    :return: sanitized string
    :rtype: str
    """

    return string.encode(CHAR_SET, errors='ignore').decode(CHAR_SET)
