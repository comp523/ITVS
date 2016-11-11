"""
Database abstraction class for handling storage of Posts and Comments
"""

import atexit
import os
import MySQLdb as dblib


from .models import (
    Comment,
    CommentFactory,
    Post,
    PostFactory,
    WordDayFactory
)
from .query import (
    Condition,
    InsertQuery,
    SelectQuery,
    UpdateQuery
)


COMMENT_FIELDS = Comment.get_fields()

POST_FIELDS = Post.get_fields()

ENTRY_TABLE = "entries"

ENTRY_COLUMNS = dict(COMMENT_FIELDS, **POST_FIELDS)

_database = None


@staticmethod
def connect(**kwargs):
    """
    Opens the connection to the database.
    """
    global _database

    if not _database:

        if not kwargs:
            kwargs = {
                "host": os.environ['OPENSHIFT_MYSQL_DB_HOST'],
                "port": int(os.environ['OPENSHIFT_MYSQL_DB_PORT']),
                "user": os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
                "passwd": os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
                "db": 'ranalyze'
            }

        _database = dblib.connect(**kwargs)


def add_update_entry( entry):
    """
    Add an entry to the database or update if it already exists.
    """

    if _entry_exists(entry):
        _update_entry(entry)
    else:
        _add_entry(entry)


def create_db():
    """
    Create a new, pre-formatted database
    """

    connection = dblib.connect(host=os.environ['OPENSHIFT_MYSQL_DB_HOST'],
        port=int(os.environ['OPENSHIFT_MYSQL_DB_PORT']),
        user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
        passwd=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
        db='ranalyze')

    cursor = connection.cursor()

    queries = ("DROP TABLE IF EXISTS {}".format(ENTRY_TABLE),
               """
               CREATE TABLE {} (
               id varchar(255) PRIMARY KEY, permalink text, root_id text,
               up_votes integer, up_ratio real, time_submitted integer,
               time_updated integer, posted_by text, title text,
               subreddit text, external_url text, text_content text,
               parent_id varchar(255), gilded integer, deleted integer,
               FOREIGN KEY(parent_id) REFERENCES entries(id)
               )
               """.format(ENTRY_TABLE))

    for query in queries:
        cursor.execute(query)

    connection.commit()
    connection.close()

def execute_query(query, commit=False, transpose=True):
    """
    Executes a given Query, optionally committing changes. Results are
    transposed by default.
    """

    cursor = _database.cursor(dblib.cursors.DictCursor)
    cursor.execute(query.sql, query.params)
    results = cursor.fetchall()
    if commit:
        _database.commit()
    if transpose:
        results = [_row_to_entry(e) for e in results]
    return results


def get_entry(entry_id):
    """
    Retrieve an item from the database where column=value.
    """

    query = SelectQuery(table=ENTRY_TABLE,
                        where=Condition("id", entry_id))
    result = execute_query(query)
    if len(result) > 0:
        return result[0]
    return None


def get_latest_post(subreddit):

    condition = (Condition("permalink", "IS NOT", None)
                 & Condition("subreddit", subreddit.lower()))

    query = SelectQuery(table=ENTRY_TABLE,
                        columns=["id", "MAX(time_submitted)"],
                        where=condition)
    print(query.sql)
    print(query.params)
    result = execute_query(query, transpose=False)[0]

    if result['id'] is None:
        return None

    latest_id = result['id']

    return get_entry(latest_id)


def _add_entry( entry):
    """
    Add an item to the database
    """

    query = InsertQuery(table=ENTRY_TABLE,
                        values=entry.dict)
    execute_query(query, commit=True)


@atexit.register
def _close():
    """
    Close the database connection
    """

    _database.close()


def _entry_exists(entry):
    """
    Check if an entry exists in the database
    """

    query = SelectQuery(table=ENTRY_TABLE,
                        columns="COUNT(*)",
                        where=Condition("id", entry.id))
    result = execute_query(query, transpose=False)[0]
    return result['COUNT(*)'] == 1


def _row_to_entry(row):
    if row is None:
        return None
    factory = CommentFactory if row["permalink"] is None else PostFactory
    return factory.from_row(row)


def _update_entry(entry):
    """
    Update an existing entry in the database.
    """

    query = UpdateQuery(table=ENTRY_TABLE,
                        values=entry.dict,
                        where=Condition("id", entry.id))

    execute_query(query, commit=True)


class DatabaseError(Exception):
    """
    Exceptions raised for errors in database I/O.
    """

    def __init__(self, message):
        """
        Generate a new DatabaseError with a given message
        """

        self.message = message
        super().__init__(self.message)


class UnknownColumnError(DatabaseError):
    """
    Exceptions raised for invalid column
    """

    _FORMAT = "No such column `{column}` in table `{table}`"

    def __init__(self, column, table):
        super().__init__(self._FORMAT.format(column=column, table=table))
