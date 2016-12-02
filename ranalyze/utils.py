"""
Common utilities
"""

import datetime
import re
from math import floor
from string import printable
from .constants import CHAR_SET

EPOCH = datetime.datetime.utcfromtimestamp(0)


def date_to_timestamp(date):
    """
    convert datetime.datetime or datetime.date object to Unix timestamp
    """
    if isinstance(date, datetime.date):
        date = datetime.datetime.combine(date, datetime.time.min)
    return floor((date - EPOCH).total_seconds())


def timestamp_to_str(timestamp):

    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime('%Y-%m-%d %H:%M:%S')


def iso_to_date(iso):
    """
    Convert ISO formatted date string to datetime.date object
    """
    return datetime.datetime.strptime(iso, "%Y-%m-%d").date()


INVALID_RE = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)


def sanitize_string(text):
    """
    Remove any characters that would be represented as 4 bytes in UTF8, to
    prevent MYSQL errors.
    
    :param text:
    :type text: str
    :return: sanitized string
    :rtype: str
    """

    return INVALID_RE.sub(u'', text)
