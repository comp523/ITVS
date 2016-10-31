"""
Tool to import a set of permalinks from a csv into the database
"""

import csv
from argparse import SUPPRESS

from .database import Database
from .config import (
    Config,
    DictConfigModule
)
from .scrape import fetch_post


class ImportConfig(DictConfigModule):
    _arguments_dict = {
        "database": {
            ("-d", "--database-file"): {
                "help": ("analysis data will be written "
                         "to this SQLite file"),
                "type": str
            }
        },
        "import": {
            ("-i", "--import"): {
                "help": "file to import permalinks from",
                "type": str,
                "required": True
            }
        },
        "development": {
            ("--debug",): {
                "help":SUPPRESS,
                "dest": "debug",
                "action": "store_true"
            }
        }
    }

    def get_runner(self):
        
        return main


def main():
    """
    Read in csv file, put permalinks in csv file in the database.
    """

    config = Config.get_instance()

    database = Database(config["database_file"], config["debug"])
    
    with open(config["import"], newline='') as importcsv:
        csvreader = csv.reader(importcsv)
        for row in csvreader:
            for cell in row:
                for entry in fetch_post(cell):
                    database.add_update_entry(entry)
