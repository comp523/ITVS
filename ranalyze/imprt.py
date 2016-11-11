"""
Tool to import a set of permalinks from a csv into the database
"""

import csv

from .database import add_update_entry, connect
from .scrape import fetch_post


def imprt(import_file):
    """
    Read in csv file, put permalinks in csv file in the database.
    """

    connect()
    
    with open(import_file, newline='') as importcsv:
        csvreader = csv.reader(importcsv)
        for row in csvreader:
            for cell in row:
                for entry in fetch_post(cell):
                    add_update_entry(entry)
