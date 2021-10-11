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
    settg = _settings()
    _reach_tcp_or_skip(settg.HOSTNAME, settg.PORT)

    # password from the settings file has precedence, fall back to env or skip the test
    # and print which password has been used (will be shown in case a test fails):
    if settg.PASSWORD is not None:
        password = settg.PASSWORD
        print(f"{__name__}: Using OMERO password from settings file.")
    elif "OMERO_PASSWORD" in os.environ:
        print(f"{__name__}: Using OMERO_PASSWORD environment variable.")
        password = os.environ["OMERO_PASSWORD"]
    else:
        pytest.skip("no password found to connect to OMERO")

    conn = omero.gateway.BlitzGateway(
        settg.USERNAME,
        password,
        host=settg.HOSTNAME,
        port=settg.PORT,
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
