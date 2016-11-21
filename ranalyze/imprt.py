
                    
"""
Tool to import a set of permalinks from a csv into the database
"""

import csv

from .database import add_update_object, connect, ENTRY_TABLE
from .scrape import fetch_post


def importfile(fname):
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


def main():
    """
    Read in csv file, put permalinks in csv file in the database.
    """
    if __name__ == '__main__':
        config = Config.get_instance()
        importfile(config['import'])
