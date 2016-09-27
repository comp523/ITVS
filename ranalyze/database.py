"""
Database abstraction class for handling storage of Posts and Comments
"""

import sqlite3
import atexit
from .utils import date_to_timestamp
from typing import List
import os

class Database:
    """
    Database wrapper for reading and writing posts and comments to a database.
    Currently implements a SQLite database.
    """

    DATABASE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 "reddit-data.db")

    COMMENT_TABLE = "comments"

    COMMENT_COLUMNS = {"id", "post_id", "parent_id", "reddit_comment_id",
                       "posted_by", "date_posted", "up_votes"}

    POST_TABLE = "posts"

    POST_COLUMNS = {"id", "permalink", "up_votes", "up_ratio", "date_posted",
                    "date_updated", "posted_by", "controversiality",
                    "external_url", "self_text", "gilded"}

    debug_mode = False  # Prints all sql statements if True

    def __init__(self):
        """
        Opens the connection to the database.
        """

        self._database = sqlite3.connect(self.DATABASE_FILE)
        self._database.row_factory = sqlite3.Row
        atexit.register(self._close)

    def add_update_comment(self, comment_data: dict):
        """
        Add a comment to the database or update if it already exists.
        """

        for column in comment_data.keys():
            if column not in self.COMMENT_COLUMNS:
                raise DatabaseError(DatabaseError.UNKNOWN_COLUMN_ERROR.format(
                    column=column, table=self.COMMENT_TABLE))

        comment = self._get_item(table=self.POST_TABLE,
                                 column="post_id",
                                 value=comment_data["post_id"])
        if comment is None:
            self._add_item(self.COMMENT_TABLE, comment_data)
        else:
            comment_data["id"] = comment["id"]
            self._update_item(self.COMMENT_TABLE, comment_data)

    def add_update_post(self, post_data: dict):
        """
        Add a post to the database or update if it already exists.
        """

        for column in post_data.keys():
            if column not in self.POST_COLUMNS:
                raise DatabaseError(DatabaseError.UNKNOWN_COLUMN_ERROR.format(
                    column=column, table=self.POST_TABLE))

        post = self._get_item(table=self.POST_TABLE,
                              column="permalink",
                              value=post_data["permalink"])
        if post is None:
            self._add_item(self.POST_TABLE, post_data)
        else:
            post_data["id"] = post["id"]
            self._update_item(self.POST_TABLE, post_data)

    def get_comment(self, id: int=None, reddit_comment_id: str=None) -> sqlite3.Row:
        """
        Retrieve a comment by id or reddit_comment_id.
        """

        if id is None and reddit_comment_id is None:
            raise DatabaseError(DatabaseError.INVALID_IDENTIFIER_ERROR.format(
                get_type="comment",
                identifiers="id, reddit_comment_id"
            ))

        column = "id" if reddit_comment_id is None else "reddit_comment_id"
        value = id if reddit_comment_id is None else reddit_comment_id

        return self._get_item(table=self.COMMENT_TABLE,
                              column=column,
                              value=value)

    def get_comments(self, post_id: int=None, parent_id: int=None,
                     posted_by: str=None, date_posted_range: tuple=None,
                     up_range: tuple=None) -> List[sqlite3.Row]:
        """
        Retrieve multiple comments filtering by one of more parameters.
        date_posted_range and up_range are both specified with tuples in the
        format (start, end), indicating a range of [start, end], i.e. inclusive.
        date_posted_range takes datetime.date objects to specify start and end.
        If either start or end is set to None, the range will be treated as a
        lower or upper limit, respectively.
        """

        conditions = []
        values = {}

        if post_id is not None:
            conditions.append("post_id=:post_id")
            values["post_id"] = post_id

        if parent_id is not None:
            conditions.append("parent_id=:parent_id")
            values["parent_id"] = parent_id

        if posted_by is not None:
            conditions.append("posted_by=:posted_by")
            values["posted_by"] = posted_by

        if date_posted_range is not None:
            if date_posted_range[0] is not None:
                conditions.append("date_posted>=:date_range_start")
                timestamp = date_to_timestamp(date_posted_range[0])
                values["date_range_start"] = timestamp
            if date_posted_range[1] is not None:
                conditions.append("date_posted<=:date_range_stop")
                timestamp = date_to_timestamp(date_posted_range[1])
                values["date_range_stop"] = timestamp

        if up_range is not None:
            if up_range[0] is not None:
                conditions.append("up_votes>=:up_range_start")
                values["up_range_start"] = up_range[0]
            if up_range[1] is not None:
                conditions.append("up_votes<=:up_range_stop")
                values["up_range_stop"] = up_range[1]

        return self._get_items(self.COMMENT_TABLE, conditions, values)

    def get_post(self, id: int=None, permalink: str=None) -> sqlite3.Row:
        """
        Retrieve a post by id or permalink.
        """

        if id is None and permalink is None:
            raise DatabaseError(DatabaseError.INVALID_IDENTIFIER_ERROR.format(
                get_type="post",
                identifiers="id, permalink"
            ))

        column = "id" if permalink is None else "permalink"
        value = id if permalink is None else permalink

        return self._get_item(table=self.POST_TABLE,
                              column=column,
                              value=value)

    def get_posts(self, date_posted_range: tuple=None, posted_by: str=None,
                  ratio_range: tuple=None, up_range: tuple=None) -> List[sqlite3.Row]:
        """
        Retrieve multiple posts filtering by one of more parameters.
        date_posted_range, ratio_range, and up_range are each specified with
        tuples in the format (start, end), indicating a range of [start, end],
        i.e. inclusive. date_posted_range takes datetime.date objects to specify
        start and end. If either start or end is set to None, the range will be
        treated as a lower or upper limit, respectively.
        """

        conditions = []
        values = {}

        if posted_by is not None:
            conditions.append("posted_by=:posted_by")
            values["posted_by"] = posted_by

        if date_posted_range is not None:
            if date_posted_range[0] is not None:
                conditions.append("date_posted>=:date_range_start")
                timestamp = date_to_timestamp(date_posted_range[0])
                values["date_range_start"] = timestamp
            if date_posted_range[1] is not None:
                conditions.append("date_posted<=:date_range_stop")
                timestamp = date_to_timestamp(date_posted_range[1])
                values["date_range_stop"] = timestamp

        if up_range is not None:
            if up_range[0] is not None:
                conditions.append("up_votes>=:up_range_start")
                values["up_range_start"] = up_range[0]
            if up_range[1] is not None:
                conditions.append("up_votes<=:up_range_stop")
                values["up_range_stop"] = up_range[1]

        if ratio_range is not None:
            if ratio_range[0] is not None:
                conditions.append("up_ratio>=:ratio_range_start")
                values["ratio_range_start"] = ratio_range[0]
            if ratio_range[1] is not None:
                conditions.append("up_ratio<=:ratio_range_stop")
                values["ratio_range_stop"] = ratio_range[1]

        return self._get_items(self.POST_TABLE, conditions, values)

    def _add_item(self, table: str, item_data: dict):
        """
        Add an item to the database
        """

        sql_statement = "INSERT INTO {table} ({columns}) VALUES ({values})"
        columns, placeholders = self._dict_to_sql(item_data, "i")
        self._execute_sql(sql_statement.format(table=table,
                                               columns=columns,
                                               values=placeholders),
                          item_data, commit=True)

    def _close(self):
        """
        Close the database connection
        """

        self._database.close()

    @staticmethod
    def _dict_to_sql(dictionary: dict, mode: str) -> (str, str):
        """
        Convert a dict to sql.

        In insert mode (mode="i"), the dict is parsed into two strings: a list
        of columns, and a list of placeholders. They are used together in an
        INSERT statement.

        In update mode (mode="u"), the dict is parsed into a single string for
        use in an UPDATE statement.
        """

        if mode is "i":
            columns = ", ".join(dictionary.keys())
            placeholders = ":" + ", :".join(dictionary.keys())
            return columns, placeholders
        elif mode is "u":
            return ", ".join(["{}=:{}".format(i, i) for i in dictionary.keys()])

    def _execute_sql(self, sql: str, params=(), commit: bool=False) -> sqlite3.Cursor:
        """
        Gets a new cursor, executes given sql, with given params. Optionally
        commits changes to the database.
        """

        if self.debug_mode:
            print("SQL:", sql)
            print("params:", params)

        cursor = self._database.cursor()
        cursor.execute(sql, params)
        if commit:
            self._database.commit()
        return cursor

    def _get_item(self, table: str, column: str, value: str) -> sqlite3.Row:
        """
        Retrieve an item from the database where column=value.
        """

        sql_statement = "SELECT * FROM {table} WHERE {column}=?"
        return self._execute_sql(sql_statement.format(table=table,
                                                      column=column),
                                 (value,)).fetchone()

    def _get_items(self, table: str, conditions: List[str], values: dict) -> List[sqlite3.Row]:
        """
        Retrieve multiple items from the database matching all supplied
        conditions. Conditions should be in SQL syntax. values supplies
        the actual data for placeholders in the conditions.
        """

        sql_statement = "SELECT * FROM {table} WHERE {conditions}"
        conditions = " AND ".join(conditions)
        return self._execute_sql(sql_statement.format(table=table,
                                                      conditions=conditions),
                                 values).fetchall()

    def _update_item(self, table: str, item_dict: dict):
        """
        Update an existing entry in the database.
        """

        sql_statement = ("UPDATE {table} SET {columns} "
                         "WHERE id=:id")
        columns = self._dict_to_sql(item_dict, "u")
        self._execute_sql(sql_statement.format(table=table,
                                               columns=columns),
                          item_dict, commit=True)


class DatabaseError(Exception):
    """
    Exception raised for errors in database I/O.
    """

    INVALID_IDENTIFIER_ERROR = ("Missing/invalid identifier for get_{get_type},"
                                " only one of ({identifiers}) is allowed")

    UNKNOWN_COLUMN_ERROR = "No such column `{column}` in table `{table}`"

    def __init__(self, message: str):
        """
        Generate a new DatabaseError with a given message
        """

        self.message = message
