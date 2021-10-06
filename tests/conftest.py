"""Module-wide fixtures for testing hrm-omero."""

import logging
import os
import pytest
from _pytest.logging import caplog as _caplog

import omero.gateway
from loguru import logger


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


### OMERO connection related fixtures


@pytest.fixture(scope="module")
def omero_conn():
    """Establish a connection to on OMERO instance.

    The fixture will try to import the test settings file or skip the entire test in
    case importing fails.

    Then it will try to figure out a password to use for the OMERO connection with the
    entry "password" from the settings file having highest priority. In case that entry
    doesn't exist, it will check if the environment has a variable 'OMERO_PASSWORD' and
    use that one instead.

    If none of the above methods to establish the password works, the entire test will
    be skipped.

    Then it will prepare the connection using the values from the test settings file and
    finally will try to establish the connection. In case that step fails again the
    entire test will be skipped.

    Eventually the connection object will be properly closed again.

    If the test is skipped for any of the above described reasons a corresponding
    message will be shown explaining the reason for skipping the test.
    """
    _imported = pytest.importorskip(
        modname="omero_test_settings",
        reason="Couldn't find 'omero_test_settings.py' to import!",
    )
    settings = _imported.SETTINGS

    # password from the settings file has precedence, fall back to env or skip the test
    # and print which password has been used (will be shown in case a test fails):
    if "password" in settings:
        print(f"{__name__}: Using OMERO password from settings file.")
        password = settings["password"]
    elif "OMERO_PASSWORD" in os.environ:
        print(f"{__name__}: Using OMERO_PASSWORD environment variable.")
        password = os.environ["OMERO_PASSWORD"]
    else:
        pytest.skip("no password found to connect to OMERO")

    conn = omero.gateway.BlitzGateway(
        settings["username"],
        password,
        host=settings["hostname"],
        port=settings["port"],
        secure=True,
        useragent="HRM-OMERO.connector",
    )

    try:
        conn.connect()
        print(f"{__name__}: Fixture established connection to OMERO.")

        yield conn

    except Exception as err:  # pylint: disable-msg=broad-except
        pytest.skip(f"establishing the connection to OMERO failed: {err}")

    finally:
        conn.close()
        print(f"{__name__}: Fixture successfully closed the connection to OMERO.")
