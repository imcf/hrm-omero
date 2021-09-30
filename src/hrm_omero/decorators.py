"""Decorator functions."""

import functools
from loguru import logger as log


def connect_and_set_group(func):
    """Decorator ensuring the connection is established and the group context is set.

    This decorator is specifically made for functions that require an established
    connection to OMERO as well as the group for the connection / session to be switched
    explicitly.

    In addition it also validates the `id_str` parameter to make sure only values are
    accepted that will potentially work with the respective OMERO calls.

    IMPORTANT: this decorator alters the signature of the function that is called - it
    is **required** for the function to be decorated to have the first three parameters
    of its signature to be `conn, obj_type, obj_id` as described in the **Other
    Parameters** section below.

    Other Parameters
    ----------------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    obj_type : str
        A valid OMERO object type, e.g. `Image` or `Dataset`.
    obj_id : str or int
        An OMERO object id, e.g. `1573559`.
    """

    @functools.wraps(func)
    def wrapper_connect_and_set_group(conn, id_str, *args, **kwargs):
        """Inner wrapper function for the `connect_and_set_group` decorator.

        Parameters
        ----------
        conn : omero.gateway.BlitzGateway
            The OMERO connection object.
        id_str : str
            The ID of an OMERO object (e.g. `G:23:Image:42`).

        Raises
        ------
        RuntimeError
            Raised in case the OMERO connection can't be established.
        ValueError
            Raised in case a malformed `id_str` was given.
        """
        # the connection might be closed (e.g. after importing an image), so force
        # re-establish it (note that `conn._connected` might even report the wrong
        # state initially, or also after reconnecting!)
        conn.connect()
        if not conn._connected:  # pylint: disable-msg=protected-access
            raise RuntimeError("Failed to (re-)establish connection to OMERO!")
        log.success("Successfully (re-)connected to OMERO!")

        # validate id_str:
        try:
            group_type, group_id, obj_type, obj_id = id_str.split(":")
            int(group_id)  # raises a TypeError if cast to int fails
            int(obj_id)  # raises a TypeError if cast to int fails
            if group_type != "G":
                raise ValueError
            if obj_type not in [
                "Image",
                "Dataset",
                "Project",
                "ExperimenterGroup",
            ]:
                raise ValueError
        except (ValueError, TypeError):
            # pylint: disable-msg=raise-missing-from
            raise ValueError("Malformed `id_str`, expecting `G:[gid]:[type]:[iid]`!")

        log.trace(f"Validated ID string: group={group_id}, {obj_type}={obj_id}")

        # set the OMERO group for the current connection session:
        conn.setGroupForSession(group_id)
        log.debug(f"Set OMERO session group to [{group_id}].")

        func(conn, obj_type, obj_id, *args, *kwargs)

    return wrapper_connect_and_set_group
