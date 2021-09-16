"""Functions related to direct interaction with OMERO."""

import logging
from omero.gateway import BlitzGateway


def connect(user, passwd, host, port=4064):
    """Establish the connection to an OMERO server.

    NOTE: this does NOT check credentials - it only talks to the OMERO server to create
    the connection object. To verify a login, use `check_credentials()`.

    Parameters
    ----------
    user : str
        The OMERO user name (e.g. `demo_user_01`).
    passwd : str
        The corresponding OMERO user password.
    host : str
        The OMERO server hostname or IP address.
    port : int, optional
        The OMERO port number, by default 4064.

    Returns
    -------
    omero.gateway.BlitzGateway
        The OMERO connection object.
    """
    conn = BlitzGateway(
        user, passwd, host=host, port=port, secure=True, useragent="HRM-OMERO.connector"
    )
    conn.connect()
    logging.debug("Created new OMERO connection [user=%s].", user)
    return conn


def check_credentials(conn):
    """Check if supplied credentials are valid and print a message to stdout.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The connection object as returned by `connect()`.

    Returns
    -------
    bool
        True if connecting was successful (i.e. credentials are correct), False
        otherwise.
    """
    connected = conn.connect()
    if connected:
        print("Success logging into OMERO with user ID %s" % conn.getUserId())
    else:
        print("ERROR logging into OMERO.")
    return connected
