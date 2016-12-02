"""
Tool to import a set of permalinks from a csv into the database
"""

import csv

from .constants import ENTRY_TABLE, IMPORT_TABLE
from .database import add_update_object, connect, execute_query
from .scrape import fetch_post
from .query import (
    Condition,
    InsertQuery,
    SelectQuery,
    UpdateQuery,
    DeleteQuery
)
CHUNK_SIZE = 100

def import_file(fname):
    """
    import a csv file with the given name
    """
    
    connect()
    
    with open(fname, newline='') as importcsv:
        csvreader = csv.reader(importcsv)
        for row in csvreader:
            for cell in row:
                for entry in fetch_post(cell):
                    add_update_object(entry, ENTRY_TABLE)

                    
def schedule_for_import(fname):
    """
    insert permalinks into table for later import
    """
    connect()
    count = 0
    with open(fname, newline='') as importcsv:
        csvreader = csv.reader(importcsv)
        for row in csvreader:
            for cell in row:

                add_update_object({"permalink" : cell}, IMPORT_TABLE)
                count += 1
    return count


def import_from_table():
    """
    retrieve permalinks from import table and scrape data into database
    """
    connect()
    count = 1
    while count > 0:
        dataQuery = SelectQuery(IMPORT_TABLE) #, limit=CHUNK_SIZE)
        data = execute_query(dataQuery, transpose=False)
        for row in data:
            for entry in fetch_post(row["permalink"]):
                add_update_object(entry, ENTRY_TABLE)

# Hasn't been tested with DeleteQuery, almost certainly won't work without testing				
				
#			deleteQuery = DeleteQuery(IMPORT_TABLE, where={permalink: row[0]})
        count = 0
#		countQuery = SelectQuery(IMPORT_TABLE, "count(*)")
#		count = execute_query(countQuery)
