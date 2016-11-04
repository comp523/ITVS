"""
Common utilities
"""

from datetime import datetime
from math import floor

EPOCH = datetime.utcfromtimestamp(0)


def date_to_timestamp(date):
    """
    convert datetime.datetime or datetime.date object to Unix timestamp
    """
    return floor((date - EPOCH).total_seconds())


def dict_deep_merge(dest, src):

    for key in src.keys():
        if key in dest and type(dest[key]) is dict:
            dict_deep_merge(dest[key], src[key])
        elif key in dest and type(dest) is list:
            dest[key].append(src[key])
        elif src[key] is not None:
            dest[key] = src[key]


def iso_to_date(iso):
    """
    Convert ISO formatted date string to datetime.date object
    """
    return datetime.strptime(iso, "%Y-%m-%d").date()
