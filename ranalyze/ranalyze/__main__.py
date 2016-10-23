"""
Main control flow for the package
"""

from .config import Config
from .database import DatabaseConfigModule
from .scrape import ScrapeConfigModule
from .search import SearchConfigModule
from .imprt import ImportConfig


def main():

    config = Config.get_instance()

    config.register_module(DatabaseConfigModule("create-db"))
    config.register_module(ScrapeConfigModule("scrape"))
    config.register_module(SearchConfigModule("search"))
    config.register_module(ImportConfig("import"))

    runner = config.parse()

    runner()

if __name__.endswith("__main__"):
    main()
