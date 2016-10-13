"""
Submodule providing database search functionality
"""

from json import dumps
from .config import Config, DictConfigModule
from .database import Database
from .utils import iso_to_date


class SearchConfigModule(DictConfigModule):

    _arguments_dict = {
        "database": {
            ("-d", "--database-file"): {
                "help": "SQLite database to search",
                "required": True,
                "type": str
            }
        },
        "search criteria": {
            ("-a", "--after"): {
                "help": "only search posts on or after a specified date"
            },
            ("-b", "--before"): {
                "help": "only search posts on or before a specified date"
            },
            ("-k", "--keyword"): {
                "action": "append",
                "help": "specify search keywords/phrases",
                "required": True
            },
            ("-s", "--subreddit"): {
                "action": "append",
                "help": "restrict search to specified subreddits"
            }
        }
    }

    def get_runner(self):
        return main


def main():

    config = Config.get_instance()
    database = Database(config["database_file"])

    keywords = ["%{}%".format(k) for k in config["keyword"]]

    options = {
        "distinct": True,
        "text_content": ("LIKE", keywords)
    }

    if config["subreddit"]:
        options["subreddit"] = config["subreddit"]

    date_range = (config["after"], config["before"])

    options["time_submitted_range"] = tuple(iso_to_date(d)
                                            if d is not None else None
                                            for d in date_range)

    entries = database.get_entries(**options)

    print(dumps([e.dict for e in entries]))
