"""Module-wide fixtures for testing hrm-omero."""

import hashlib
import json
import logging
import sys

import pytest
from _pytest.logging import caplog as _caplog  # pylint: disable-msg=unused-import
from loguru import logger

### common "private" functions


def _stderr(message):
    """Simple wrapper to print to stderr.

    This is required as several tests need to capture stdout (as this is integral
    behavior of the underlying code to push stuff there) and therefore using the
    standard `print()` call would make those tests fail as output will be polluted.
    """
    print(message, file=sys.stderr)


def _sha1(filename):
    """Calculate the SHA1 sum of a file.

    Parameters
    ----------
    filename : str
        The full path to the file to calculate the checksum for.

    Returns
    -------
    str
        The SHA1 checksum in hexadecimal notation.
    """
    buf_size = 65536  # read file in 64kB chunks

    sha1sum = hashlib.sha1()

    with open(filename, "rb") as infile:
        while True:
            data = infile.read(buf_size)
            if not data:
                break
            sha1sum.update(data)

    digest = sha1sum.hexdigest()
    print(f"sha1({filename}): {digest}")
    return digest


### pytest setup ###


def pytest_addoption(parser):
    """Add a command line option '--online' to pytest."""
    parser.addoption(
        "--online",
        action="store_true",
        default=False,
        help="enable online tests communicating to a real OMERO instance",
    )


def pytest_collection_modifyitems(config, items):
    """Add the 'skip' marker to tests decorated with 'pytest.mark.online'."""
    if config.getoption("--online"):
        # --online given in cli: do not skip online tests
        return
    skip_online = pytest.mark.skip(reason="need --online option to run")
    for item in items:
        if "online" in item.keywords:
            item.add_marker(skip_online)


### caplog special loguru setup ###


@pytest.fixture
def caplog(_caplog):
    """Fixture adding a sink that propagates Loguru messages to the builtin logging.

    This ensures that pytest will be able to capture log messages via the "normal"
    `caplog` fixture that are actually logged through Loguru.
    """

    class PropagateHandler(logging.Handler):
        """Helper class to propagate emitted messages to the `logging` module."""

        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropagateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)


### commonly used functions, provided as a fixture


@pytest.fixture
def json_is_equal():
    """Fixture comparing two objects for equality after JSON serialization.

    Provides a function that takes two arguments of any (serializable) type. In case
    any of the arguments is of type `str` it will first be deserialized (assuming the
    content is JSON). Eventually the serialized version of both arguments will be tested
    for equality.
    """

    def json_is_equal_inner(expected, received):
        """Test JSON representation of two objects for equality.

        Parameters
        ----------
        expected : any
            The "expected" object, must be JSON-serializable.
        received : any
            The "received" object, must be JSON-serializable.

        Returns
        -------
        bool
            True in case the JSON representation of both arguments is identical, False
            otherwise.
        """
        if isinstance(expected, str):
            _stderr(f"EXPECTED RAW\n---\n{expected}\n---")
            expected = json.loads(expected)
        serialized_exp = json.dumps(expected, indent=4, sort_keys=True)

        if isinstance(received, str):
            _stderr(f"RECEIVED RAW\n---\n{received}\n---")
            received = json.loads(received)
        serialized_rec = json.dumps(received, indent=4, sort_keys=True)

        _stderr(f"EXPECTED\n---\n{serialized_exp}\n---")
        _stderr(f"RECEIVED\n---\n{serialized_rec}\n---")
        return serialized_rec == serialized_exp

    return json_is_equal_inner


@pytest.fixture
def sha1():
    """Fixture to generate the SHA1 sum of a file."""
    return _sha1


@pytest.fixture
def cli_args():
    """Construct the list of arguments required by `hrm_omero.cli.run_task()`.

    Parameters
    ----------
    action : str
        The *action* name.
    action_args : list(str), optional
        A list of additional arguments to be put after the action parameter.
    hrm_conf : str, optional
        Path to an `hrm.conf` configuration file. If skipped or empty the
        default value `resources/hrm.conf` will be used.
    user : str, optional
        The user name to put as an argument for the `--user` parameter. If
        skipped or empty the default value `pytest` will be used.
    dry_run : bool, optional
        Whether to add the `--dry-run` flag to the argument list as the second
        argument, by default False.

    Returns
    -------
    list(str)
    """

    def _cli_args(action, action_args=[], hrm_conf="", user="", dry_run=False):
        if not hrm_conf:
            hrm_conf = "resources/hrm.conf"
        if not user:
            user = "pytest"

        base_args = [
            "-vvvv",
            "--conf",
            hrm_conf,
            "--user",
            user,
            action,
        ]
        if dry_run:
            base_args.insert(1, "--dry-run")

        args = base_args + action_args
        print(f"{__name__}: assembled CLI args = {args}")

        return args

    return _cli_args
