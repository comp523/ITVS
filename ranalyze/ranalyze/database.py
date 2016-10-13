"""
Database abstraction class for handling storage of Posts and Comments
"""

import atexit
import sqlite3

from typing import Callable, List, Tuple, Union
from .common_types import DateRange, IntRange
from .config import Config, ConfigModule
from .entry import (
    Comment,
    CommentFactory,
    Entry,
    Post,
    PostFactory
)
from .utils import date_to_timestamp


class Database(object):
    """
    Database wrapper for reading and writing posts and comments to a database.
    Currently implements a SQLite database.
    """

    COMMENT_FIELDS = Comment.get_fields()

    POST_FIELDS = Post.get_fields()

    ENTRY_TABLE = "entries"

    ENTRY_COLUMNS = {**COMMENT_FIELDS, **POST_FIELDS}

    def __init__(self, database_file: str, debug_mode: bool=False):
        """
        Opens the connection to the database.
        """

        # Prints all sql statements if True
        self._debug_mode = debug_mode

        self._database = sqlite3.connect(database_file)
        self._database.row_factory = sqlite3.Row
        atexit.register(self._close)

    def add_update_entry(self, entry: Entry):
        """
        Add an entry to the database or update if it already exists.
        """

        if self._entry_exists(entry):
            self._update_entry(entry)
        else:
            self._add_entry(entry)

    @staticmethod
    def create_db(filename: str):
        """
        Create a new, pre-formatted database
        """

        connection = sqlite3.connect(filename)

        cursor = connection.cursor()

        queries = ("DROP TABLE IF EXISTS {}".format(Database.ENTRY_TABLE),
                   """
                   CREATE TABLE {} (
                   id text PRIMARY KEY, permalink text UNIQUE, root_id text,
                   up_votes integer, up_ratio real, time_submitted integer,
                   time_updated integer, posted_by text, title text,
                   subreddit text, external_url text, text_content text,
                   parent_id text, gilded integer, deleted integer,
                   FOREIGN KEY(parent_id) REFERENCES entries(id)
                   )
                   """.format(Database.ENTRY_TABLE))

        for query in queries:
            cursor.execute(query)

        connection.commit()
        connection.close()

    def get_entry(self, entry_id: str) -> Entry:
        """
        Retrieve an item from the database where column=value.
        """

        sql_statement = "SELECT * FROM {} WHERE id=?".format(self.ENTRY_TABLE)
        row = self._execute_sql(sql_statement, (entry_id,)).fetchone()
        return Database._row_to_entry(row)

    def get_entries(self, columns: List[str]=None, distinct: bool=False,
                    up_vote_range: IntRange=None, up_ratio_range: IntRange=None,
                    time_submitted_range: DateRange=None,
                    **kwargs) -> List[Entry]:
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
            operand = value[0] if type(value) is tuple else "="
            value = value[1] if type(value) is tuple else value
            if type(value) is list:
                conditions.append("({})".format(" OR ".join([
                    "{column} {operand} :{column}_{i}".format(
                        column=key,
                        operand=operand,
                        i=i) for i in range(len(value))
                ])))
                for i in range(len(value)):
                    values["{}_{}".format(key, i)] = value[i]
            else:
                conditions.append("{column} {operand} :{column}".format(
                    column=key,
                    operand=operand
                ))
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

        columns = "*" if columns is None else ", ".join(columns)

        select = "SELECT"
        if distinct:
            select += " DISTINCT"

        sql_statement = "{select} {columns} FROM {table} WHERE {conditions}"
        conditions = " AND ".join(conditions)
        rows = self._execute_sql(sql_statement.format(table=self.ENTRY_TABLE,
                                                      conditions=conditions,
                                                      columns=columns,
                                                      select=select),
                                 values).fetchall()
        return [Database._row_to_entry(row) for row in rows]

    def get_latest_post(self, subreddit: str) -> Entry:

        sql_statement = """
        SELECT id, MAX(time_submitted) FROM {table}
        WHERE permalink IS NOT NULL
        AND subreddit=?
        """.format(table=Database.ENTRY_TABLE)

        params = subreddit.lower(),

        result = self._execute_sql(sql_statement, params).fetchone()

        if result is None:
            return None

        latest_id = result[0]

        return self.get_entry(latest_id)

    def _add_entry(self, entry: Entry):
        """
        Add an item to the database
        """

        sql_statement = "INSERT INTO {table} ({columns}) VALUES ({values})"
        columns, placeholders = self._dict_to_sql(entry.dict, "i")
        self._execute_sql(sql_statement.format(table=self.ENTRY_TABLE,
                                               columns=columns,
                                               values=placeholders),
                          entry.dict, commit=True)

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

    def _entry_exists(self, entry: Entry) -> bool:
        """
        Check if an entry exists in the database
        """

        sql_statement = "SELECT COUNT(*) FROM {table} WHERE id=:id".format(
            table=Database.ENTRY_TABLE
        )

        row = self._execute_sql(sql_statement, {"id": entry.id}).fetchone()

        return row[0] == 1

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

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> Entry:
        if row is None:
            return None
        factory = CommentFactory if row["permalink"] is None else PostFactory
        return factory.from_row(row)

    def _update_entry(self, entry: Entry):
        """
        Update an existing entry in the database.
        """

        sql_statement = "UPDATE {table} SET {columns} WHERE id=:id"
        columns = self._dict_to_sql(entry.dict, "u")
        self._execute_sql(sql_statement.format(table=self.ENTRY_TABLE,
                                               columns=columns),
                          entry.dict, commit=True)


class DatabaseError(Exception):
    """
    Exceptions raised for errors in database I/O.
    """

    def __init__(self, message: str):
        """
        Generate a new DatabaseError with a given message
        """

        self.message = message
        super().__init__(message)


class UnknownColumnError(DatabaseError):
    """
    Exceptions raised for invalid column
    """

    _FORMAT = "No such column `{column}` in table `{table}`"

    def __init__(self, column: str, table: str):
        super().__init__(self._FORMAT.format(column=column, table=table))


class DatabaseConfigModule(ConfigModule):

    def initialize(self):

        parser = self._get_subparser()
        parser.add_argument("name",
                            help="File name of the SQLite database to create")

    def get_runner(self) -> Callable:

        return create_db


def create_db():

    config = Config.get_instance()
    Database.create_db(config["name"])

    print("Created `{}` successfully".format(config["name"]))
