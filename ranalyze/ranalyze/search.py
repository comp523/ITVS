"""
Submodule providing database search functionality
"""

from json import dumps
from .config import Config, DictConfigModule
from .database.database import Database
from .database.query import Condition, SelectQuery
from .utils import iso_to_date


KEYWORD_COLUMNS = {"text_content", "title"}


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
            ("-c", "--columns"): {
                "help": "space-delimited list of columns to include in results",
                "nargs": "+"
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

    condition = Condition()

    for word in keywords:
        keyword_condition = Condition()
        for column in KEYWORD_COLUMNS:
            keyword_condition |= Condition(column, "LIKE", word)
        condition |= keyword_condition

    if config["subreddit"]:
        subreddit_condition = Condition()
        for sub in config["subreddit"]:
            subreddit_condition |= Condition("subreddit", sub)
        condition &= subreddit_condition

    if config["after"]:
        date = iso_to_date(config["after"])
        condition &= Condition("time_submitted", ">=", date)

    if config["before"]:
        date = iso_to_date(config["before"])
        condition &= Condition("time_submitted", "<=", date)

    columns = ", ".join(config["columns"]) if config["columns"] else "*"

    query = SelectQuery(table=Database.ENTRY_TABLE,
                        distinct=True,
                        where=condition,
                        columns=columns)

    entries = database.execute_query(query, transpose=False)

    print(dumps([dict(zip(e.keys(), e)) for e in entries]))
