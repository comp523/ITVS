"""
Module for giving progress feedback in the command line
"""

import atexit


class Progress:
    """
    Static only class for outputting update-able feedback to stdout
    """

    _params = {}

    format = ""

    def __init__(self):
        """
        Disable initialization
        """

        error_message = "Progress objects cannot be instantiated"

        raise NotImplementedError(message=error_message)


    @staticmethod
    @atexit.register
    def freeze():
        """
        Freeze the current progress. Future calls to update will be on the
        next line.
        """

        print("")

    @staticmethod
    def update(**kwargs):
        """
        Update the progress with new values
        """

        # Update any params specified in kwargs
        Progress._params.update(kwargs)

        # Print with trailing carriage return to keep output on one line
        print(Progress.format.format(**Progress._params), end="\r")
