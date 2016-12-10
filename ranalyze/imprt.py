"""
Tool to import a set of permalinks from a csv into the database
"""

import csv

from .constants import ENTRY_TABLE, IMPORT_CHUNK_SIZE, IMPORT_TABLE
from .database import add_update_object, execute_query
from .scrape import fetch_post
from .query import Condition, SelectQuery, DeleteQuery, InsertQuery

def import_file(fname):
    """
    import a csv file with the given name
    """
    
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

    count = 0
    print (fname)
    with open(fname, newline='') as importcsv:
        csvreader = csv.reader(importcsv)
        print ("b")
        for row in csvreader:
            print ((row,))
            for cell in row:
                print ("c")
                q = InsertQuery(IMPORT_TABLE, {"permalink":cell})
                execute_query(q, commit=True)
                count += 1
    print (count)
    return count


def import_from_table():
    """
    retrieve permalinks from import table and scrape data into database
    """

    count = 1
    while count > 0:
        dataQuery = SelectQuery(IMPORT_TABLE, limit=IMPORT_CHUNK_SIZE)
        data = execute_query(dataQuery, transpose=False)
        for row in data:
            for entry in fetch_post(row["permalink"]):
                add_update_object(entry, ENTRY_TABLE)				
            deleteQuery = DeleteQuery(IMPORT_TABLE, where=Condition("permalink", row["permalink"]))
            execute_query(deleteQuery, commit=true)
        count = 0
        countQuery = SelectQuery(IMPORT_TABLE, "count(*) as numleft")
        count = execute_query(countQuery, transpose=False)[0]['numleft']
