"""Miscellaneous functions used across the package."""

from loguru import logger as log


def printlog(level, message):
    """Simple wrapper to push a message to stdout and logging.

    Note that something very similiar (or identical) could be achieved by adding a log
    handler that emits to stdout.

    Parameters
    ----------
    level : str
        The log level of the message as defined by loguru.
    message : str
        The message to be printed and logged.
    """
    print(message)
    log.log(level, message)


def parse_id_str(id_str):
    """Parse and validate an ID string of the form `G:[gid]:[type]:[iid]`

    Parameters
    ----------
    id_str : str
        The ID of an OMERO object, e.g.
        * `G:23:Image:42`
        * `G:4:Dataset:765487`

    Returns
    -------
    group_id, obj_type, obj_id
        A triplet of `str` denoting the group ID, object type and object ID.

    Raises
    ------
    ValueError
        Raised in case a malformed `id_str` was given.
    """
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

    return group_id, obj_type, obj_id
