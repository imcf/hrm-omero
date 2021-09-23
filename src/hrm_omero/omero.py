"""Functions related to direct interaction with OMERO."""

# pylint: disable-msg=consider-using-f-string

import yaml
from loguru import logger as log
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
    log.warning("'connect()' is DEPRECATED, will be removed in an upcoming release!")
    conn = BlitzGateway(
        user, passwd, host=host, port=port, secure=True, useragent="HRM-OMERO.connector"
    )
    conn.connect()
    group = conn.getGroupFromContext()
    log.debug("Created new OMERO connection [user={}, group={}].", user, group.getId())
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


def extract_image_id(fname):
    """Parse the YAML returned by an 'omero import' call and extract the image ID.

    Parameters
    ----------
    fname : str
        The path to the `yaml` file to parse.

    Returns
    -------
    int or None
        The OMERO ID of the newly imported image, e.g. `1568386` or `None` in case
        parsing the file failed for any reason.
    """
    try:
        with open(fname, "r", encoding="utf-8") as stream:
            parsed = yaml.safe_load(stream)
        if len(parsed[0]['Image']) != 1:
            msg = f"Unexpected YAML retrieved from OMERO, unable to parse:\n{parsed}"
            print(msg)
            raise SyntaxError(msg)
        image_id = parsed[0]['Image'][0]
    except Exception as err:  # pylint: disable-msg=broad-except
        msg = f"Error parsing imported image ID from YAML output: {err}"
        print(msg)
        log.error(msg)
        return None

    return image_id
