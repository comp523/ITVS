"""
Module for giving progress feedback in the command line
"""

import atexit


class Progress:

    def __init__(self, output_format: str):
        """
        Initialize progress feedback
        """

        self.output_format = output_format
        self.params = {}

    @staticmethod
    @atexit.register
    def freeze():
        """
        Freeze the current progress. Future calls to update will be on the
        next line.
        """

        print("")

    def update(self, **kwargs):
        """
        Update the progress with new values
        """

        self.params.update(kwargs)

        print(self.output_format.format(**self.params), end="\r")
