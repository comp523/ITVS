"""
Configuration processor for ranalyze

Configuration sources (in order of precedence):

 - Command line arguments
 - .yaml config file (specified with -c command line argument)
"""

import sys
import yaml

from argparse import (ArgumentParser, SUPPRESS)
from .database import Database
from datetime import (datetime, date)
from itertools import chain
from re import compile
from typing import Tuple


class Config:
    """
    Configuration parser
    """

    _CLI_ARGUMENTS = {
        "date range": {
            ("-a", "--after"): {
                "help": "only analyze posts on or after this date",
                "type": str
            },
            ("-b", "--before"): {
                "help": ("only analyze posts on or before "
                         "this date, defaults to today"),
                "type": str
            }
        },
        "subreddit selection": {
            ("-s", "--subreddit"): {
                "action": "append",
                "dest": "subreddits",
                "help": ("subreddit to analyze, may be a single value, "
                         "or a space-delimited list"),
                "nargs": "+",
                "type": str
            }
        },
        "database": {
            ("-d", "--database-file"): {
                "help": ("analysis data will be written "
                         "to this SQLite file"),
                "type": str
            }
        },
        "configuration": {
            ("-c", "--config-file"): {
                "help": "load configuration from file",
                "type": str
            }
        },
        "development": {
            ("--debug",): {
                "help": SUPPRESS,
                "dest": "debug",
                "action": "store_true"
            }
        }
    }

    _config = {
        "database_file": None,
        "date_range": None,
        "debug": False,
        "subreddits": None
    }

    _config_processors = {
        "database_file": None,
        "date_range":
            lambda date_range: {key: Config._validate_date(value) for
                                key, value in date_range.items()},
        "debug": lambda debug: bool(debug),
        "subreddits":
            lambda sub_list:
                set(Config._SANITIZE_SUBREDDIT_REGEX.match(sub).group(1)
                    for sub in sub_list),
    }

    _DATE_REGEX = compile(r"^\d{4}-\d{2}-\d{2}$")
    _SANITIZE_SUBREDDIT_REGEX = compile(r"^(?:/?r?/?)([^/]*)/?$")

    @staticmethod
    def get_config() -> dict:
        """
         Retrieve the configuration.
        """

        return Config._config.copy()

    @staticmethod
    def initialize():
        """
        Initialize the config state from all configured sources.
        """

        # handle create-db sub-command

        if len(sys.argv) > 1 and sys.argv[1] == "create-db":
            Database.create_db(sys.argv[2])
            print("Database `{}` created successfully.".format(sys.argv[2]))
            exit()

        parser = ArgumentParser("ranalyze")

        cli_config, config_file = Config._parse_cli_args(parser)

        if config_file is not None:
            with open(config_file) as file:
                yaml_config = Config._parse_yaml(file.read())
        else:
            yaml_config = None

        config = Config.get_config()

        config_order = (yaml_config, cli_config)

        for key, value in config.items():
            for config_src in config_order:
                if config_src is not None and config_src[key] is not None:
                    if value is not None and type(value) is list:
                        config[key].extend(config_src[key])
                    elif value is not None and type(value) is dict:
                        Config._merge_configs(config[key], config_src[key])
                    else:
                        config[key] = config_src[key]

        try:
            cleaned_config = Config._clean_config(config)
            Config._validate_config(config)
            Config._config = cleaned_config

        except ConfigError as error:
            parser.error(error.message)

    @staticmethod
    def _clean_config(config: dict):
        """
        Run each config value through its pre-processor if one is defined.
        Pre-processors are defined in Config._config_processors
        """

        if (config["date_range"] is not None
           and ("before" not in config["date_range"]
                or config["date_range"]["before"] is None)):

            config["date_range"]["before"] = datetime.today().date().isoformat()

        for key, value in config.items():
            if Config._config_processors[key] is not None and value is not None:
                config[key] = Config._config_processors[key](value)

        return config

    @staticmethod
    def _validate_config(config: dict):
        """
        Validate the config ensuring required values have been set.
        """

        if config["database_file"] is None:
            raise MissingParameterError("database_file")

        if config["subreddits"] is None:
            raise MissingParameterError("subreddits")

        if (config["date_range"] is None or "after" not in config["date_range"]
           or config["date_range"]["after"] is None):

            raise MissingParameterError("date_range.after")

    @staticmethod
    def _parse_cli_args(parser: ArgumentParser) -> Tuple[dict, str]:
        """
        Parse command line arguments. Generates a set of subreddits to analyze,
        an inclusive date range, and an output file.

        All arguments are validated. Errors may be raised for:
        - Invalid Date Format (e.g. 9/4/2016)
        - Invalid Date (e.g. 2/30/2016)
        - Non-existent input file

        Subreddits are sanitized to remove extraneous characters:
        - leading path information (i.e. /, r/, /r/)
        - trailing slashes

        Subreddits are parsed to a set of strings
        Date range is parsed to a tuple of datetime.date objects
        Database file is untouched
        """

        config = Config.get_config()

        # Add the arguments to the parser

        for group_name, args in Config._CLI_ARGUMENTS.items():
            group = parser.add_argument_group(group_name)
            for flags, options in args.items():
                group.add_argument(*flags, **options)

        args = vars(parser.parse_args())

        if args["after"] is not None or args["before"] is not None:
            args["date_range"] = {key: args[key] for key in ("after", "before")
                                  if args[key] is not None}

        del args["after"]
        del args["before"]

        Config._merge_configs(config, args)

        return config, args["config_file"]

    @staticmethod
    def _parse_yaml(yaml_str: str) -> dict:
        """
        Parse YAML config file
        """

        config = Config.get_config()

        yaml_data = yaml.load(yaml_str)

        Config._merge_configs(config, yaml_data, flatten_lists=False)

        return config

    @staticmethod
    def _merge_configs(dst: dict, src: dict, flatten_lists: bool=True):
        """
        Merge entries in dictionary, src overwrites existing values in dst
        """

        for key, value in dst.items():
            if key in src:
                if type(src[key]) is list and flatten_lists:
                    dst[key] = chain(*src[key])
                else:
                    dst[key] = src[key]

    @staticmethod
    def _validate_date(date_str: str) -> date:
        """
        Validate format of the date string, and convert to datetime.date object

        Raises an error if:
        - date_str is in an invalid format
        - date_str represents an invalid date
        """

        if type(date_str) is date or date_str is None:
            return date_str

        if Config._DATE_REGEX.match(date_str) is None:
            raise DateError(date_str)

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise DateError(date_str)

        return date_obj


class ConfigError(Exception):
    """
    Base class for exceptions raised while processing configuration variables
    """

    def __init__(self, message: str):

        self.message = message


class DateError(ConfigError):
    """
    Exceptions regarding date range input
    """

    _FORMAT = ("{} is not a valid date, or is in an invalid format. "
               "Proper format is YYYY-MM-DD")

    def __init__(self, date_str: str):

        self.message = self._FORMAT.format(date_str)


class MissingParameterError(ConfigError):
    """
    Exceptions for missing required configuration parameters
    """

    _FORMAT = "Missing required configuration parameter `{}`"

    def __init__(self, param: str):

        self.message = self._FORMAT.format(param)
