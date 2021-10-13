"""Module-wide fixtures for testing hrm-omero."""

import os
import socket

import omero.gateway
import pytest
from _pytest.logging import caplog as _caplog  # pylint: disable-msg=unused-import

### common "private" functions


def _settings():
    """Load online test settings or skip a test."""
    try:
        from settings import common  # pylint: disable-msg=import-outside-toplevel
    except ImportError:
        pytest.skip("Couldn't import 'settings' package required for online tests!")
    return common


### commonly used functions, provided as a fixture


@pytest.fixture
def settings():
    """Load online test settings and return them."""
    return _settings()


### OMERO connection related fixtures


@pytest.fixture
def reach_tcp_or_skip(settings):
    """Skip a test if the OMERO server defined in settings can't be reached via TCP."""
    host = settings.HOSTNAME
    port = settings.PORT
    socket.setdefaulttimeout(0.5)
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    except (socket.error, socket.timeout):
        pytest.skip(f"can't reach OMERO server at {host}:{port}")


@pytest.fixture
def omeropw(monkeypatch, settings):
    """Prepare (and return) an OMERO password or skip the test.

    First the fixture checks if the test settings do have a password configured
    explicitly. If yes the environment variable 'OMERO_PASSWORD' will be monkey-patched
    using that configured value.

    If no password is configured the current environment is checked if the variable
    already exists.

    In any case of success the password will also be returned, so the fixture can be
    used via `@pytest.mark.usefixtures("omeropw")` or as a parameter of a test function.

    In case no password is found `pytest.skip()` will be called.
    """
    password = None
    # if no password was defined in the settings, check if the environment has one:
    if settings.PASSWORD is not None:
        password = settings.PASSWORD
        monkeypatch.setenv("OMERO_PASSWORD", password)
        print("Monkeypatching environment variable OMERO_PASSWORD...")
        return password

    password = os.environ.get("OMERO_PASSWORD")
    if password is None:
        pytest.skip("password for OMERO is required (via settings or environment)")
    else:
        print("Using existing OMERO_PASSWORD environment variable...")

    return password


@pytest.fixture
def omero_conn(reach_tcp_or_skip, settings, omeropw):
    """Establish a connection to on OMERO instance or skip the test.

    The fixture will prepare a connection using the values from the test
    settings file and finally will try to establish the connection. In case this
    fails `pytest.skip()` will be called to skip the test.

    Eventually the connection object will be properly closed again.
    """

    conn = omero.gateway.BlitzGateway(
        settings.USERNAME,
        omeropw,
        host=settings.HOSTNAME,
        port=settings.PORT,
        secure=True,
        useragent="HRM-OMERO.pytest",
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
