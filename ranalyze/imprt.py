"""
Tool to import a set of permalinks from a csv into the database
"""

import csv

from .constants import ENTRY_TABLE
from .database import add_update_object, connect
from .scrape import fetch_post


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
