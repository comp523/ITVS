"""
Provides Entry base class, as well as Comment and Post subclasses.
"""

import abc

from datetime import datetime
from sqlite3 import Row
from .utils import date_to_timestamp


class Entry(object, metaclass=abc.ABCMeta):
    """
    Base class for all database entries
    """

    _BASE_FIELDS = {
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

    def __init__(self, **kwargs):
        self._attrs = {key: (kwargs[key] if key in kwargs else None)
                       for key in self.get_fields()}

    def __getattr__(self, item):
        if item not in self.get_fields():
            raise NoSuchAttributeError(class_name=type(self).__name__,
                                       attribute=item)
        return self._attrs[item]

    @property
    def dict(self):
        return self._attrs.copy()

    @staticmethod
    @abc.abstractmethod
    def get_fields():
        pass


class EntryFactory(object, metaclass=abc.ABCMeta):
    """
    Base class for all Entry factories
    """

    _BASE_PRAW_MAP = {
        "deleted": lambda e: False,
        "id": lambda e: e.fullname,
        "posted_by": lambda e: str(e.author),
        "subreddit": lambda e: str(e.subreddit).lower(),
        "time_submitted": lambda e: e.created_utc,
        "time_updated": lambda e: date_to_timestamp(datetime.utcnow()),
        "up_votes": lambda e: e.ups
    }

    @classmethod
    def from_praw(cls, praw_obj):
        """
        Creates an Entry from a PrawEntry object
        """
        attrs = {}
        target, fields, praw_map = cls._get_properties()
        for key in fields:
            if key in praw_map:
                attrs[key] = praw_map[key](praw_obj)
            else:
                attrs[key] = getattr(praw_obj, key)
        return target(**attrs)

    @classmethod
    def from_row(cls, row):
        """
        Creates an Entry from an sqlite.Row object
        """
        data = {key: row[key] for key in row.keys()}
        target = cls._get_properties()[0]
        return target(**data)

    @staticmethod
    @abc.abstractmethod
    def _get_properties():
        """
        Subclass implemented method. Returns the target class, field dictionary,
        and praw conversion map (in that order)
        """
        pass


class Comment(Entry):
    """
    Class for comment entries into the database
    """

    _FIELDS = {
        **Entry._BASE_FIELDS,
        "root_id": str,
        "parent_id": str
    }

    @staticmethod
    def get_fields():
        return Comment._FIELDS


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

    @staticmethod
    def _get_properties():
        return (
            CommentFactory._TARGET,
            Comment.get_fields(),
            CommentFactory._PRAW_MAP
        )


class Post(Entry):
    """
    Class for post entries into the database
    """

    _FIELDS = {
        **Entry._BASE_FIELDS,
        "permalink": str,
        "up_ratio": float,
        "title": str,
        "external_url": str,
    }

    @staticmethod
    def get_fields() -> dict:
        return Post._FIELDS


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

    @staticmethod
    def _get_properties():
        return PostFactory._TARGET, Post.get_fields(), PostFactory._PRAW_MAP


class NoSuchAttributeError(AttributeError):
    """
    Errors for attempted access of non-existent attributes
    """

    _FORMAT = "No such attribute `{attribute}` in class `{class_name}`"

    def __init__(self, **kwargs):

        super().__init__(NoSuchAttributeError._FORMAT.format(**kwargs))
