"""
Database abstraction class for handling storage of Posts and Comments
"""

import MySQLdb
import os

from .constants import (
    CHAR_SET,
    CONFIG_TABLE,
    ENTRY_TABLE,
    FREQUENCY_TABLE,
    IMPORT_TABLE,
    SUBREDDIT_TABLE
)
from .models import (
    CommentFactory,
    ConfigEntryFactory,
    PostFactory,
    SubredditFactory,
    WordDayFactory
)
from .query import (
    Condition,
    InsertQuery,
    SelectQuery,
    UpdateQuery,
    DeleteQuery
)


def connect(**kwargs):
    """
    Opens the connection to the database.
    """

    if not kwargs:
        kwargs = {
            "host": os.environ['OPENSHIFT_MYSQL_DB_HOST'],
            "port": int(os.environ['OPENSHIFT_MYSQL_DB_PORT']),
            "user": os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
            "passwd": os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
            "db": 'ranalyze'
        }

    with MySQLdb.connect(charset=CHAR_SET, **kwargs) as database:
        query = ("SET GLOBAL sql_mode="
                 "(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
        database.execute(query)

    return MySQLdb.connect(charset=CHAR_SET, **kwargs)


def add_update_object(obj, table):
    """
    Add an Entry to the database or update if it already exists.
    :param table:
    """

    if object_exists(obj, table):
        return _update_object(obj, table)
    else:
        return _add_object(obj, table)


def create_db():
    """
    Create a new, pre-formatted database
    """

    connection = MySQLdb.connect(host=os.environ['OPENSHIFT_MYSQL_DB_HOST'],
                                 port=int(os.environ['OPENSHIFT_MYSQL_DB_PORT']),
                                 user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
                                 passwd=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
                                 db='ranalyze')

    cursor = connection.cursor()

    queries = ("DROP TABLE IF EXISTS {}".format(ENTRY_TABLE),
               "DROP TABLE IF EXISTS {}".format(FREQUENCY_TABLE),
               "DROP TABLE IF EXISTS {}".format(CONFIG_TABLE),
               "DROP TABLE IF EXISTS {}".format(IMPORT_TABLE),
               """
               CREATE TABLE {} (
               id varchar(255) PRIMARY KEY, permalink text, root_id text,
               up_votes integer, up_ratio real, time_submitted integer,
               time_updated integer, posted_by text, title text,
               subreddit text, external_url text, text_content text,
               parent_id varchar(255), gilded integer, deleted integer,
               FOREIGN KEY(parent_id) REFERENCES entries(id)
               )
               DEFAULT CHARACTER SET {}
               """.format(ENTRY_TABLE, CHAR_SET),
               """
               CREATE TABLE {} (
               id integer PRIMARY KEY AUTO_INCREMENT, word varchar(255), month integer,
               day integer, year integer, entries integer, total integer
               )
               DEFAULT CHARACTER SET {}
               """.format(FREQUENCY_TABLE, CHAR_SET),
               """
               CREATE TABLE {} (
               id integer PRIMARY KEY AUTO_INCREMENT, name varchar(255),
               value varchar(255)
               )
               DEFAULT CHARACTER SET {}
               """.format(CONFIG_TABLE, CHAR_SET),
               """
               CREATE TABLE {} (
               permalink text)
               DEFAULT CHARACTER SET {}
               """.format(IMPORT_TABLE, CHAR_SET),
               # We need a trigger to insert the integer unix timestamp
               """
               CREATE TABLE {} (
               name varchar(20) PRIMARY KEY, scraping integer(1) DEFAULT 0,
               last_scraped integer, added integer NULL
               )
               DEFAULT CHARACTER SET {};
               delimiter $$
               CREATE TRIGGER tr_sub_added BEFORE INSERT ON {} FOR EACH ROW
               BEGIN
                 if (new.added is null)
                 then
                   set new.added = unix_timestamp();
                 end if;
               end $$
               delimiter ;
               """.format(SUBREDDIT_TABLE, CHAR_SET, SUBREDDIT_TABLE)
               )

    for query in queries:
        cursor.execute(query)

    connection.commit()
    connection.close()


def execute_query(query, commit=False, transpose=True, only_id=False):
    """
    Executes a given Query, optionally committing changes. Results are
    transposed by default.
    """
    connection = connect()
    try:
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query.sql, query.params)
        if commit:
            connection.commit()
        if only_id:
            return cursor.lastrowid
        results = cursor.fetchall()
        if transpose:
            results = [_row_to_object(o) for o in results]
        return results
    finally:
        connection.close()


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
                        where=condition,
                        group="id")

    result = execute_query(query, transpose=False)

    if not result or result[0]["id"] is None:
        return None

    latest_id = result[0]["id"]

    return get_entry(latest_id)


def remove_object_by_id(_id, table):
    cond = Condition('id', _id)
    query = DeleteQuery(table=table,
                        where=cond)
    execute_query(query, commit=True)


def _add_object(obj, table):
    """
    Add an item to the database
    """

    query = InsertQuery(table=table,
                        values=obj)
    return execute_query(query, commit=True, only_id=True)

'''
@atexit.register
def _close():
    """
    Close the database connection
    """
    if _database:
        _database.close()
'''

def object_exists(obj, table):
    """
    Check if an Entry exists in the database
    """

    query = SelectQuery(table=table,
                        columns="COUNT(*)",
                        where=Condition(obj.KEY, getattr(obj, obj.KEY)))
    result = execute_query(query, transpose=False)[0]
    return result['COUNT(*)'] == 1


def _row_to_object(row):
    """

    :param row:
    :return:
    :rtype: ModelObject
    """
    if row is None:
        return None
    elif "word" in row.keys():
        factory = WordDayFactory
    elif "value" in row.keys():
        factory = ConfigEntryFactory
    elif "scraping" in row.keys():
        factory = SubredditFactory
    elif row["permalink"] is None:
        factory = CommentFactory
    else:
        factory = PostFactory
    return factory.from_row(row)


def _update_object(obj, table):
    """
    Update an existing Entry in the database.
    """

    values = obj.dict

    if obj.KEY in values:
        del values[obj.KEY]

    query = UpdateQuery(table=table,
                        values=values,
                        where=Condition(obj.KEY, getattr(obj, obj.KEY)))

    return execute_query(query, commit=True, only_id=True)


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
