"""Miscellaneous functions used across the package."""

from loguru import logger as log


def printlog(level, message):
    """Simple wrapper to push a message to stdout and logging.

    Note that something very similiar (or identical) could be achieved by adding a log
    handler that emits to stdout.

    Parameters
    ----------
    level : str
        The log level of the message as defined by loguru.
    message : str
        The message to be printed and logged.
    """
    print(message)
    log.log(level, message)
