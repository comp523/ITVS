"""
Module for parsing configuration from various sources.
"""

import abc

from argparse import ArgumentParser
import yaml


class AlternateSource(object, metaclass=abc.ABCMeta):
    """
    Base class for alternate sources of configuration parameters.
    """

    @property
    @abc.abstractmethod
    def config_dict(self):
        """
        Subclasses should implement this method to parse and return their
        configuration parameters as a dictionary.
        """


class YAMLSource(AlternateSource):
    """
    Implements an AlternateSource parsed from a YAML configuration file
    """

    def __init__(self, yaml_filename):

        self._yaml_filename = yaml_filename

    @property
    def config_dict(self):

        with open(self._yaml_filename) as file:
            yaml_data = yaml.load(file)

        return yaml_data


class ConfigError(BaseException):
    """
    Class for handling errors in processing or accessing configuration values
    """

    def __init__(self, message):

        self.message = message


class ConfigModule(object, metaclass=abc.ABCMeta):
    """
    Base class for submodules to extend and define their own configuration
    parameters and sources.
    """

    def __init__(self, name: str):

        self.name = name

    @abc.abstractmethod
    def get_runner(self):
        """
        Subclasses should implement this function to return a reference to their
        respective main methods (or module 'runners')
        """
        pass

    @abc.abstractmethod
    def initialize(self):
        """
        Subclasses should implement this function to set up their respective
        subparsers
        """
        pass

    def _get_subparser(self):

        if not hasattr(self, "_subparser"):
            config = Config.get_instance()
            self._subparser = config.sub_parsers.add_parser(self.name)

        return self._subparser


class DictConfigModule(ConfigModule, metaclass=abc.ABCMeta):
    """
    Convenience class for modules to specify their config in a pre-formatted
    dictionary
    """

    def __init__(self, name):
        super().__init__(name)

    def initialize(self):

        parser = self._get_subparser()

        DictConfigModule._add_arguments_from_dict(parser, self._arguments_dict)

    @staticmethod
    def _add_arguments_from_dict(parser, arguments):
        """
        Adds all arguments to a parser from a pre-formatted dict.

        Format:
        - Each key in `arguments` the name of an argument group
        - Each value is a dictionary containing that group's arguments (gr_args)
        - Each key in `gr_args` is a tuple containing command line flags for
          that argument
        - Each value in `gr_args` is a dictionary of arguments to pass as
          keyword arguments to ArgumentParser.add_argument
        """

        for group_name, gr_args in arguments.items():
            group = parser.add_argument_group(group_name)
            for flags, options in gr_args.items():
                group.add_argument(*flags, **options)

    @property
    @abc.abstractmethod
    def _arguments_dict(self):
        """
        Subclasses should implement this to pass the arguments dictionary,
        formatted as specified in DictConfigModule._add_arguments_from_dict
        """
        pass


class Config(object):

    _instance = None

    def __init__(self):

        self.modules = []
        self.parser = ArgumentParser("ranalyze")
        self.sub_parsers = self.parser.add_subparsers(dest="function")
        self._config = {}

    def __getitem__(self, item):

        return self._config[item]

    def add_source(self, source, overwrite=False):
        """
        Add an AlternateSource to the configuration. If overwrite is set to
        true, then conflicting values from the new alternate source will
        overwrite existing values, except lists which will always be
        concatenated.
        """

        for key, value in source.config_dict.items():
            if key in self._config and type(self._config[key]) is list:
                self._config[key].extend(value)
            elif key not in self._config or overwrite:
                self._config[key] = value

    def error(self, message):

        self.parser.error(message)

    @staticmethod
    def get_instance():

        if Config._instance is None:
            Config._instance = Config()

        return Config._instance

    def register_module(self, module):

        module.initialize()
        self.modules.append(module)

    def parse(self, args=None):
        """
        Parse configuration from the command line first. Once the valid,
        registered sub-command is determined. Configuration parameters from
        any additional sources are parsed as follows:
         - Command line parameters take highest precedence
         - After command line, precedence is determined by the order in which
           the sources were registered.
         - Conflicts are settled by precedence except:
           - Lists are concatenated
        """

        parsed = (self.parser.parse_args(args) if args
                  else self.parser.parse_args())

        # find corresponding submodule

        submodule = None

        for module in self.modules:
            if module.name == parsed.function:
                submodule = module

        if not submodule:
            self.parser.error("no function selected")

        self._config = vars(parsed)

        return submodule.get_runner()
