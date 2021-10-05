"""Functions related to direct interaction with OMERO."""

import yaml
from loguru import logger as log
import omero.gateway
from Ice import ConnectionLostException  # pylint: disable-msg=no-name-in-module

from .decorators import connect_and_set_group
from .misc import printlog


def connect(user, passwd, host, port=4064):
    """Establish the connection to an OMERO server.

    DEPRECATED function, rather use BlitzGateway's `connect()` in a context manager or
    in a try/finally block to ensure the connection is properly `close()`d in any case!

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
    conn = omero.gateway.BlitzGateway(
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
        The OMERO connection object.

    Returns
    -------
    bool
        True if connecting was successful (i.e. credentials are correct), False
        otherwise.
    """
    connected = conn.connect()
    if connected:
        printlog("SUCCESS", f"Connected to OMERO [user ID: {conn.getUserId()}].")
    else:
        printlog("WARNING", "ERROR logging into OMERO.")

    try:
        group = conn.getGroupFromContext()
        log.debug(f"User's default group is {group.getId()} ({group.getName()}).")
    except ConnectionLostException:
        log.warning("Getting group context failed, password might be wrong!")
        return False

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
        if len(parsed[0]["Image"]) != 1:
            msg = f"Unexpected YAML retrieved from OMERO, unable to parse:\n{parsed}"
            printlog("ERROR", msg)
            raise SyntaxError(msg)
        image_id = parsed[0]["Image"][0]
    except Exception as err:  # pylint: disable-msg=broad-except
        printlog("ERROR", f"Error parsing imported image ID from YAML output: {err}")
        return None

    return image_id


@connect_and_set_group
def add_annotation_keyvalue(conn, obj_type, obj_id, annotation):
    """Add a key-value "map" annotation to an OMERO object.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    obj_type : str
        A valid OMERO object type, e.g. `Image` or `Dataset`.
    obj_id : str or int
        An OMERO object id, e.g. `1573559`.
    annotation : dict(dict)
        The map annotation as returned by `hrm_omero.hrm.parse_summary()`.

    Returns
    -------
    bool
        True in case of success, False otherwise.

    Raises
    ------
    RuntimeError
        Raised in case re-establishing the OMERO connection fails.
    """
    target_obj = conn.getObject(obj_type, obj_id)
    if target_obj is None:
        log.warning(f"Unable to identify target object {obj_id} in OMERO!")
        return False

    for section in annotation:
        namespace = f"Huygens Remote Manager - {section}"
        map_ann = omero.gateway.MapAnnotationWrapper(conn)
        map_ann.setValue(annotation[section].items())
        map_ann.setNs(namespace)
        map_ann.save()
        target_obj.linkAnnotation(map_ann)
        log.debug(f"Added key-value annotation using namespace [{namespace}].")

    log.success(f"Successfully added annotation to {obj_type}:{obj_id}.")

    return True


@connect_and_set_group
def new_project(conn, id_str, proj_name):
    """Create a new Project in OMERO.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    id_str : str
        The ID of an OMERO object, e.g. `G:4:Experimenter:23`
    proj_name : str
        The name of the project to be created.
    """
    raise NotImplementedError("Creating Projects is not yet implemented.")


@connect_and_set_group
def new_dataset(conn, id_str, ds_name):
    """Create a new Project in OMERO.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    id_str : str
        The ID of an OMERO object, e.g. `G:4:Project:123`
    ds_name : str
        The name of the dataset to be created.
    """
    raise NotImplementedError("Creating Datasets is not yet implemented.")
