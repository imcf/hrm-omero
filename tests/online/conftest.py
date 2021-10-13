"""Module-wide fixtures for testing hrm-omero."""

import os
import socket

import omero.gateway
import pytest
from _pytest.logging import caplog as _caplog  # pylint: disable-msg=unused-import

### common "private" functions


def _reach_tcp_or_skip(host, port):
    """Skip a test if a TCP connection to the given host and port CAN'T be established.

    Parameters
    ----------
    host : str
        Host name (DNS) or IP address.
    port : int
        The TCP port number to connect to.
    """
    socket.setdefaulttimeout(0.5)
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    except (socket.error, socket.timeout):
        pytest.skip(f"can't reach OMERO server at {host}:{port}")


def _settings():
    """Load online test settings or skip a test."""
    try:
        from settings import common  # pylint: disable-msg=import-outside-toplevel
    except ImportError:
        pytest.skip("Couldn't import 'settings' package required for online tests!")
    return common


### commonly used functions, provided as a fixture


@pytest.fixture
def reach_tcp_or_skip():
    """Fixture function wrapper to check if a host is reachable on a given port."""
    return _reach_tcp_or_skip


@pytest.fixture
def settings():
    """Load online test settings and return them."""
    return _settings()


### OMERO connection related fixtures


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
def omero_conn(settings, omeropw):
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
    _reach_tcp_or_skip(settings.HOSTNAME, settings.PORT)

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
