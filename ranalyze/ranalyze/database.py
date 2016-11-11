"""
Database abstraction class for handling storage of Posts and Comments
"""

import atexit
import os
#if 'OPENSHIFT_MYSQL_DB_HOST' in os.environ:
import MySQLdb as dblib
#else:
#  import sqlite3 as dblib

from .config import Config, ConfigModule
from .entry import (
    Comment,
    CommentFactory,
    Post,
    PostFactory
)
from .query import (
    Condition,
    InsertQuery,
    SelectQuery,
    UpdateQuery
)


class Database(object):
    """
    Database wrapper for reading and writing posts and comments to a database.
    Currently implements a SQLite database.
    """

    COMMENT_FIELDS = Comment.get_fields()

    POST_FIELDS = Post.get_fields()

    ENTRY_TABLE = "entries"

    ENTRY_COLUMNS = dict(COMMENT_FIELDS, **POST_FIELDS)

    def __init__(self, database_file, debug_mode=False):
        """
        Opens the connection to the database.
        """

        # Prints all sql statements if True
        self._debug_mode = debug_mode

        #self._database = dblib.connect(database_file)
        self._database = dblib.connect(host=os.environ['OPENSHIFT_MYSQL_DB_HOST'],
            port=int(os.environ['OPENSHIFT_MYSQL_DB_PORT']),
            user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
            passwd=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
            db='ranalyze')
        # DEPRECATED sqlite code
        # self._database.row_factory = dblib.Row
        atexit.register(self._close)

    def add_update_entry(self, entry):
        """
        Add an entry to the database or update if it already exists.
        """

        if self._entry_exists(entry):
            self._update_entry(entry)
        else:
            self._add_entry(entry)

    @staticmethod
    def create_db(filename):
        """
        Create a new, pre-formatted database
        """

        connection = dblib.connect(host=os.environ['OPENSHIFT_MYSQL_DB_HOST'],
            port=int(os.environ['OPENSHIFT_MYSQL_DB_PORT']),
            user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
            passwd=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
            db='ranalyze')

        cursor = connection.cursor()

        queries = ("DROP TABLE IF EXISTS {}".format(Database.ENTRY_TABLE),
                   """
                   CREATE TABLE {} (
                   id varchar(255) PRIMARY KEY, permalink text, root_id text,
                   up_votes integer, up_ratio real, time_submitted integer,
                   time_updated integer, posted_by text, title text,
                   subreddit text, external_url text, text_content text,
                   parent_id varchar(255), gilded integer, deleted integer,
                   FOREIGN KEY(parent_id) REFERENCES entries(id)
                   )
                   """.format(Database.ENTRY_TABLE))

        for query in queries:
            cursor.execute(query)

        connection.commit()
        connection.close()

    def execute_query(self, query, commit=False, transpose=True):
        """
        Executes a given Query, optionally committing changes. Results are
        transposed by default.
        """

        if self._debug_mode:
            print("SQL:", query.sql)
            print("params:", query.params)

        cursor = self._database.cursor(dblib.cursors.DictCursor)
        cursor.execute(query.sql, query.params)
        results = cursor.fetchall()
        if commit:
            self._database.commit()
        if transpose:
            results = [Database._row_to_entry(e) for e in results]
        return results

    def get_entry(self, entry_id):
        """
        Retrieve an item from the database where column=value.
        """

        query = SelectQuery(table=Database.ENTRY_TABLE,
                            where=Condition("id", entry_id))
        result = self.execute_query(query)
        if len(result) > 0:
            return result[0]
        return None

    def get_latest_post(self, subreddit):

        condition = (Condition("permalink", "IS NOT", None)
                     & Condition("subreddit", subreddit.lower()))

        query = SelectQuery(table=Database.ENTRY_TABLE,
                            columns=["id", "MAX(time_submitted)"],
                            where=condition)
        print(query.sql)
        print(query.params)
        result = self.execute_query(query, transpose=False)[0]

        if result['id'] is None:
            return None

        latest_id = result['id']

        return self.get_entry(latest_id)

    def _add_entry(self, entry):
        """
        Add an item to the database
        """

        query = InsertQuery(table=Database.ENTRY_TABLE,
                            values=entry.dict)
        self.execute_query(query, commit=True)

    def _close(self):
        """
        Close the database connection
        """

        self._database.close()

    def _entry_exists(self, entry):
        """
        Check if an entry exists in the database
        """

        query = SelectQuery(table=Database.ENTRY_TABLE,
                            columns="COUNT(*)",
                            where=Condition("id", entry.id))
        result = self.execute_query(query, transpose=False)[0]
        return result['COUNT(*)'] == 1

    @staticmethod
    def _row_to_entry(row):
        if row is None:
            return None
        factory = CommentFactory if row["permalink"] is None else PostFactory
        return factory.from_row(row)

    def _update_entry(self, entry):
        """
        Update an existing entry in the database.
        """

        query = UpdateQuery(table=Database.ENTRY_TABLE,
                            values=entry.dict,
                            where=Condition("id", entry))

        self.execute_query(query, commit=True)


class DatabaseError(Exception):
    """
    Exceptions raised for errors in database I/O.
    """

    def __init__(self, message):
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

    def __init__(self, column, table):
        super().__init__(self._FORMAT.format(column=column, table=table))


class DatabaseConfigModule(ConfigModule):

    def initialize(self):

        parser = self._get_subparser()
        parser.add_argument("name",
                            help="File name of the SQLite database to create")

    def get_runner(self):

        return create_db


def create_db():

    config = Config.get_instance()
    Database.create_db(config["name"])

    print("Created `{}` successfully".format(config["name"]))
