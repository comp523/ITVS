"""
Provides Entry base class, as well as Comment and Post subclasses.
"""

import abc

from .common_types import PrawEntry
from datetime import datetime
from sqlite3 import Row
from typing import Type
from .utils import date_to_timestamp


class Entry(object, metaclass=abc.ABCMeta):
    """
    Base class for all database entries
    """

    BASE_FIELDS = {
        "id": str,
        "up_votes": int,
        "time_submitted": datetime,
        "time_updated": datetime,
        "posted_by": str,
        "subreddit": str,
        "text_content": str,
        "gilded": bool,
        "deleted": bool
    }

    FIELDS = None

    def __init__(self, **kwargs):
        self._attrs = {key: (kwargs[key] if key in kwargs else None)
                       for key in self.FIELDS}

    def __getattr__(self, item):
        if item not in self.FIELDS:
            raise NoSuchAttributeError(class_name=type(self).__name__,
                                       attribute=item)
        return self._attrs[item]

    @property
    def dict(self) -> dict:
        return self._attrs.copy()


class EntryFactory(object, metaclass=abc.ABCMeta):
    """
    Base class for all Entry factories
    """

    _BASE_PRAW_MAP = {
        "deleted": lambda e: False,
        "id": lambda e: e.fullname,
        "posted_by": lambda e: str(e.author),
        "subreddit": lambda e: str(e.subreddit),
        "time_submitted": lambda e: e.created_utc,
        "time_updated": lambda e: date_to_timestamp(datetime.utcnow()),
        "up_votes": lambda e: e.ups
    }

    _PRAW_MAP = None

    _TARGET = None

    @classmethod
    def from_praw(cls, praw_obj: PrawEntry) -> Entry:
        attrs = {}
        for key in cls._TARGET.FIELDS:
            if key in cls._PRAW_MAP:
                attrs[key] = cls._PRAW_MAP[key](praw_obj)
            else:
                attrs[key] = getattr(praw_obj, key)
        return cls._TARGET(**attrs)

    @staticmethod
    def from_row(row: Row) -> Entry:
        data = {key: row[key] for key in row.keys()}
        return Post(**data)


class Comment(Entry):
    """
    Class for comment entries into the database
    """

    FIELDS = {
        **Entry.BASE_FIELDS,
        "root_id": str,
        "parent_id": str
    }


class CommentFactory(EntryFactory):
    """
    Factory for creating Comment instances from various sources
    """

    # Converts praw.objects.Comment attributes to Comment attributes
    _PRAW_MAP = {
        **EntryFactory._BASE_PRAW_MAP,
        "root_id": lambda c: c.submission.fullname,
        "text_content": lambda c: c.body
    }

    _TARGET = Comment


class Post(Entry):
    """
    Class for post entries into the database
    """

    FIELDS = {
        **Entry.BASE_FIELDS,
        "permalink": str,
        "up_ratio": float,
        "title": str,
        "external_url": str,
    }


class PostFactory(EntryFactory):
    """
    Factory for creating Post instances from various sources
    """

    # Converts praw.objects.Submission attributes to Post attributes
    _PRAW_MAP = {
        **EntryFactory._BASE_PRAW_MAP,
        "external_url": lambda s: s.url,
        "text_content": lambda s: s.selftext,
        "up_ratio": lambda s: 0  # TODO: Implement up_ratio?
    }

    _TARGET = Post


class NoSuchAttributeError(AttributeError):
    """
    Errors for attempted access of non-existent attributes
    """

    _FORMAT = "No such attribute `{attribute}` in class `{class_name}`"

    def __init__(self, **kwargs):

        self.message = NoSuchAttributeError._FORMAT.format(**kwargs)
