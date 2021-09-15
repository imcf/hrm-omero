"""Helper functions to interact with the HRM."""

import shlex
import logging


def parse_config(filename):
    """Assemble a dict from the HRM config file (shell syntax).

    Usually, the config is located at /etc/hrm.conf and written in shell syntax as
    this file simply gets sourced by the bash init script and other shell based
    tools.

    Parameters
    ----------
    filename : str
        The name of the configuration file to be parsed.

    Returns
    -------
    dict
        A dict with the parsed configuration items.

    Raises
    ------
    SyntaxError
        Raised in case the given configuration file can't be parsed correctly.

    Example
    -------
    >>> parse_config('/etc/hrm.conf')
    ... {
    ...     'HRM_DATA': '/export/hrm_data',
    ...     'HRM_DEST': 'dst',
    ...     'HRM_HOME': '/var/www/hrm',
    ...     'HRM_LOG': '/var/log/hrm',
    ...     'HRM_SOURCE': 'src',
    ...     'OMERO_HOSTNAME': 'omero.mynetwork.xy',
    ...     'OMERO_PKG': '/opt/OMERO/OMERO.server',
    ...     'OMERO_PORT': '4064',
    ...     'PHP_CLI': '/usr/local/php/bin/php',
    ...     'SUSER': 'hrm'
    ... }
    """
    config = dict()
    with open(filename, "r") as file:
        body = file.read()

    lexer = shlex.shlex(body)
    lexer.wordchars += "-./"
    while True:
        token = lexer.get_token()
        if token is None or token == "":
            break
        # it's valid sh syntax to use a semicolon to join lines, so accept it:
        if token == ";":
            continue
        # we assume entries of the following form:
        # KEY="some-value"
        key = token
        try:
            equals = lexer.get_token()
            assert equals == "="
        except AssertionError:
            raise SyntaxError(
                "Can't parse %s, invalid syntax in line %s "
                "(expected '=', found '%s')." % (filename, lexer.lineno, equals)
            )
        except Exception as err:  # pylint: disable-msg=broad-except
            logging.warning("Error parsing config: %s", err)
        value = lexer.get_token()
        value = value.replace('"', "")  # remove double quotes
        value = value.replace("'", "")  # remove single quotes
        config[key] = value
    logging.debug("Successfully parsed [%s].", filename)
    return config


def check_config(config):
    """Check the config dict for required entries.

    Parameters
    ----------
    config : dict
        A dict with a parsed configuration, as returned by `parse_hrm_conf()`.

    Raises
    ------
    SyntaxError
        Raised in case one of the required configuration items is missing.
    """
    required = ["OMERO_PKG", "OMERO_HOSTNAME"]
    for entry in required:
        if entry not in config:
            raise SyntaxError('Missing "%s" in the HRM config file.' % entry)
    logging.debug("HRM config file passed all checks.")
