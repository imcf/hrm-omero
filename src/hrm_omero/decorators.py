"""Decorator functions."""

import functools
from loguru import logger as log

from .misc import OmeroId


def connect_and_set_group(func):
    """Decorator ensuring the connection is established and the group context is set.

    This decorator is specifically made for functions that require an established
    connection to OMERO as well as the group for the connection / session to be switched
    explicitly.

    In addition it also checks the `omero_id` parameter and ensures it is an
    object of type `hrm_omero.misc.OmeroId`. In case the parameter received is a
    string, it will automatically create the corresponding `OmeroId` object,
    which also checks the values of the ID for sanity.

    Other Parameters
    ----------------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    omero_id : str or hrm_omero.misc.OmeroId
        The fully qualified ID of an OMERO object (e.g. `G:23:Image:42`) as
        a string or as an `hrm_omero.misc.OmeroId` object directly.
    """

    @functools.wraps(func)
    def wrapper_connect_and_set_group(conn, omero_id, *args, **kwargs):
        """Inner wrapper function for the `connect_and_set_group` decorator.

        Parameters
        ----------
        conn : omero.gateway.BlitzGateway
            The OMERO connection object.
        omero_id : str or hrm_omero.misc.OmeroId
            The fully qualified ID of an OMERO object (e.g. `G:23:Image:42`) as
            a string or as an `hrm_omero.misc.OmeroId` object directly.

        Raises
        ------
        RuntimeError
            Raised in case the OMERO connection can't be established.
        ValueError
            Raised in case a malformed `omero_id` was given.
        """
        # the connection might be closed (e.g. after importing an image), so force
        # re-establish it (note that `conn._connected` might even report the wrong
        # state initially, or also after reconnecting!)
        conn.connect()
        if not conn._connected:  # pylint: disable-msg=protected-access
            raise RuntimeError("Failed to (re-)establish connection to OMERO!")
        log.success("Successfully (re-)connected to OMERO!")

        # if the ID is passed as a string parse it into an OmeroId object:
        if isinstance(omero_id, str):
            omero_id = OmeroId(omero_id)

        # set the OMERO group for the current connection session:
        conn.setGroupForSession(omero_id.group)
        log.debug(f"Set OMERO session group to [{omero_id.group}].")

        return func(conn, omero_id, *args, *kwargs)

    return wrapper_connect_and_set_group
