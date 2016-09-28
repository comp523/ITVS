"""
Database abstraction class for handling storage of Posts and Comments
"""

import atexit
import sqlite3

from .types import (DateRange, IntRange)
from typing import (List, Tuple, Union)
from .utils import date_to_timestamp


class Database:
    """
    Database wrapper for reading and writing posts and comments to a database.
    Currently implements a SQLite database.
    """

    ENTRY_TABLE = "entries"

    ENTRY_COLUMNS = {"id", "permalink", "root_id", "up_votes", "up_ratio",
                     "time_submitted", "time_updated", "posted_by", "title",
                     "subreddit", "external_url", "text_content", "parent_id",
                     "gilded", "deleted"}

    def __init__(self, database_file: str, debug_mode: bool=False):
        """
        Opens the connection to the database.
        """

        # Prints all sql statements if True
        self._debug_mode = debug_mode

        self._database = sqlite3.connect(database_file)
        self._database.row_factory = sqlite3.Row
        atexit.register(self._close)

    def add_update_entry(self, entry_data: dict):
        """
        Add a post to the database or update if it already exists.
        """

        for column in entry_data.keys():
            if column not in self.ENTRY_COLUMNS:
                raise UnknownColumnError(column=column, table=self.ENTRY_TABLE)

        entry = self.get_entry(entry_data["id"])
        
        if entry is None:
            self._add_entry(entry_data)
        else:
            self._update_entry(entry_data)

    def get_entry(self, entry_id: str) -> sqlite3.Row:
        """
        Retrieve an item from the database where column=value.
        """

        sql_statement = "SELECT * FROM {} WHERE id=?".format(self.ENTRY_TABLE)
        return self._execute_sql(sql_statement, (entry_id,)).fetchone()

    def get_entries(self, up_vote_range: IntRange=None,
                    up_ratio_range: IntRange=None,
                    time_submitted_range: DateRange=None,
                    **kwargs) -> List[sqlite3.Row]:
        """
        Retrieve multiple items from the database matching all supplied
        conditions. Conditions should be in SQL syntax. values supplies
        the actual data for placeholders in the conditions.
        """

        conditions = []
        values = {}

        for key, value in kwargs.items():
            if key not in self.ENTRY_COLUMNS:
                raise UnknownColumnError(column=key, table=self.ENTRY_TABLE)
            conditions.append("{column}=:{column}".format(column=key))
            values[key] = value

        if up_vote_range is not None:
            if up_vote_range[0] is not None:
                conditions.append("up_votes>=:up_vote_range_start")
                values["up_vote_range_start"] = up_vote_range[0]
            if up_vote_range[1] is not None:
                conditions.append("up_votes<=:up_vote_range_end")
                values["up_vote_range_end"] = up_vote_range[1]
                
        if up_ratio_range is not None:
            if up_ratio_range[0] is not None:
                conditions.append("up_ratio>=:up_ratio_range_start")
                values["up_ratio_range_start"] = up_ratio_range[0]
            if up_ratio_range[1] is not None:
                conditions.append("up_ratio<=:up_ratio_range_end")
                values["up_ratio_range_end"] = up_ratio_range[1]
                
        if time_submitted_range is not None:
            if time_submitted_range[0] is not None:
                conditions.append("time_submitted>=:time_submitted_range_start")
                timestamp = date_to_timestamp(time_submitted_range[0])
                values["time_submitted_range_start"] = timestamp
            if time_submitted_range[1] is not None:
                conditions.append("time_submitted<=:time_submitted_range_end")
                timestamp = date_to_timestamp(time_submitted_range[1])
                values["time_submitted_range_end"] = timestamp

        sql_statement = "SELECT * FROM {table} WHERE {conditions}"
        conditions = " AND ".join(conditions)
        return self._execute_sql(sql_statement.format(table=self.ENTRY_TABLE,
                                                      conditions=conditions),
                                 values).fetchall()

    def _add_entry(self, entry_data: dict):
        """
        Add an item to the database
        """

        sql_statement = "INSERT INTO {table} ({columns}) VALUES ({values})"
        columns, placeholders = self._dict_to_sql(entry_data, "i")
        self._execute_sql(sql_statement.format(table=self.ENTRY_TABLE,
                                               columns=columns,
                                               values=placeholders),
                          entry_data, commit=True)

    def _close(self):
        """
        Close the database connection
        """

        self._database.close()

    @staticmethod
    def _dict_to_sql(dictionary: dict,
                     mode: str) -> Union[Tuple[str, str], str]:
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

    def _execute_sql(self, sql: str,
                     params=(),
                     commit: bool=False) -> sqlite3.Cursor:
        """
        Gets a new cursor, executes given sql, with given params. Optionally
        commits changes to the database.
        """

        if self._debug_mode:
            print("SQL:", sql)
            print("params:", params)

        cursor = self._database.cursor()
        cursor.execute(sql, params)
        if commit:
            self._database.commit()
        return cursor

    def _update_entry(self, entry_dict: dict):
        """
        Update an existing entry in the database.
        """

        sql_statement = "UPDATE {table} SET {columns} WHERE id=:id"
        columns = self._dict_to_sql(entry_dict, "u")
        self._execute_sql(sql_statement.format(table=self.ENTRY_TABLE,
                                               columns=columns),
                          entry_dict, commit=True)


class DatabaseError(Exception):
    """
    Exceptions raised for errors in database I/O.
    """

    def __init__(self, message: str):
        """
        Generate a new DatabaseError with a given message
        """

        self.message = message


class UnknownColumnError(DatabaseError):
    """
    Exceptions raised for invalid column
    """

    _FORMAT = "No such column `{column}` in table `{table}`"

    def __init__(self, column: str, table: str):

        self.message = self._FORMAT.format(column=column, table=table)
