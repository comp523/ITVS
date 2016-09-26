"""
Common utilities
"""

import datetime

epoch = datetime.datetime.utcfromtimestamp(0)


def date_to_timestamp(date: datetime.date) -> float:
    return (date - epoch).total_seconds() * 1000.0
