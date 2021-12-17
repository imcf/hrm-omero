"""Miscellaneous functions used across the package."""

from loguru import logger as log


class OmeroId:

    """Representation of a (group-qualified) OMERO object ID.

    The purpose of this class is to facilitate parsing and access of the
    ubiquitious target IDs denoting objects in OMERO. The constructor takes
    the common string of the form `G:[gid]:[type]:[iid]` as an input and sets
    the properties `group`, `obj_type` and `obj_id` accordingly.
    """

    def __init__(self, id_str):
        self.group = None
        self.obj_type = None
        self.obj_id = None
        self.parse_id_str(id_str)

    def parse_id_str(self, id_str):
        """Parse and validate an ID string of the form `G:[gid]:[type]:[oid]`

        The method will parse the given string and set the object's `group`, `obj_type`
        and `obj_id` values accordingly. In case for `id_str` the special value `ROOT`
        was supplied, `group` and `obj_id` will be set to `-1` whereas `obj_type` will
        be set to `BaseTree`.

        Parameters
        ----------
        id_str : str
            The ID of an OMERO object, e.g.
            * `G:23:Image:42`
            * `G:4:Dataset:765487`
            * special case `ROOT`, same as `G:-1:BaseTree:-1`

        Raises
        ------
        ValueError
            Raised in case a malformed `id_str` was given.
        """
        log.trace(f"Parsing ID string: [{id_str}]")
        if id_str == "ROOT":
            self.group = -1
            self.obj_type = "BaseTree"
            self.obj_id = -1
            log.debug(f"Converted special ID 'ROOT' to [{str(self)}].")
            return

        try:
            group_type, group_id, obj_type, obj_id = id_str.split(":")
            int(group_id)  # raises a TypeError if cast to int fails
            int(obj_id)  # raises a TypeError if cast to int fails
            if group_type != "G":
                raise ValueError(f"Invalid group qualifier '{group_type}'.")
            if obj_type not in [
                "Image",
                "Dataset",
                "Project",
                "Experimenter",
                "ExperimenterGroup",
            ]:
                raise ValueError(f"Invalid object type '{obj_type}'.")
            if int(obj_id) < 1:
                raise ValueError(f"Invalid object ID '{obj_id}'.")
        except (ValueError, TypeError) as err:
            # pylint: disable-msg=raise-missing-from
            msg = f"Malformed id_str '{id_str}', expecting `G:[gid]:[type]:[oid]`."
            raise ValueError(msg, err)

        log.debug(f"Validated ID string: group={group_id}, {obj_type}={obj_id}")
        self.group = group_id
        self.obj_type = obj_type
        self.obj_id = obj_id

    def __str__(self):
        return f"G:{self.group}:{self.obj_type}:{self.obj_id}"


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


def parse_id_str(id_str):  # pragma: no cover
    """Legacy wrapper to `hrm_omero.misc.OmeroId`."""
    log.warning(f"DEPRECATED call to {__name__}!")
    omero_id = OmeroId(id_str)
    return omero_id.group, omero_id.obj_type, omero_id.obj_id
