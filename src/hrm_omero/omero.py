"""Functions related to direct interaction with OMERO."""

from datetime import datetime, timedelta

import yaml
from Ice import ConnectionLostException  # pylint: disable-msg=no-name-in-module
from loguru import logger as log

import omero.gateway

from .decorators import connect_and_set_group
from .misc import printlog


def connect(user, passwd, host, port=4064):  # pragma: no cover
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
    log.debug("Trying to connect to OMERO...")
    connected = conn.connect()
    if connected:
        uid = conn.getUserId()
        name = conn.getUser().getName()
        printlog("SUCCESS", f"Connected to OMERO [user={name}, uid={uid}].")
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

    log.success(f"Successfully parsed Image ID from YAML: {image_id}")
    return image_id


@connect_and_set_group
def add_annotation_keyvalue(conn, omero_id, annotation):
    """Add a key-value "map" annotation to an OMERO object.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    omero_id : hrm_omero.misc.OmeroId
        The ID of the OMERO object that should receive the annotation.
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
    log.trace(f"Adding a map annotation to {omero_id}")
    target_obj = conn.getObject(omero_id.obj_type, omero_id.obj_id)
    if target_obj is None:
        log.warning(f"Unable to identify target object {omero_id} in OMERO!")
        return False

    for section in annotation:
        namespace = f"Huygens Remote Manager - {section}"
        log.trace(f"Using namespace [{namespace}] for annotation.")
        map_ann = omero.gateway.MapAnnotationWrapper(conn)
        map_ann.setValue(annotation[section].items())
        map_ann.setNs(namespace)
        map_ann.save()
        target_obj.linkAnnotation(map_ann)
        log.debug(f"Added key-value annotation using namespace [{namespace}].")

    log.success(f"Added annotation to {omero_id}.")

    return True


@connect_and_set_group
def new_project(conn, omero_id, proj_name):  # pragma: no cover
    """Create a new Project in OMERO.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    omero_id : hrm_omero.misc.OmeroId
        The ID of an OMERO object denoting an Experimenter.
    proj_name : str
        The name of the project to be created.
    """
    raise NotImplementedError("Creating Projects is not yet implemented.")


@connect_and_set_group
def new_dataset(conn, omero_id, ds_name):  # pragma: no cover
    """Create a new Project in OMERO.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    omero_id : hrm_omero.misc.OmeroId
        The ID of an OMERO object denoting a Project or an Experimenter.
    ds_name : str
        The name of the dataset to be created.
    """
    raise NotImplementedError("Creating Datasets is not yet implemented.")


def find_recently_imported(conn, ds_id, label, age=15):
    """Speculative way of identifying a recently imported image in a dataset.

    Check children of a dataset in OMERO until one is found that is matching following
    criteria:

    * the import date is not more than the specified `age` tolerance ago (in seconds)
    * the object name is matching the given label

    Usually it will hit the right object in the first iteration as `listChildren()`
    seems to give the images in reverse order of their import (newest ones first).

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    ds_id : int or int-like
        The ID of the dataset where to look for the image.
    label : str
        The label of the imported image, in the simplest case this is usually just the
        file name of the original file without any path components.
    age : int, optional
        The maximum age in seconds that the identified image object in OMERO is allowed
        to have, by default 15.

    Returns
    -------
    omero.gateway._ImageWrapper or None
        The "Image" object as returned by OMERO's BlitzGateway or None in case no image
        object matching the criteria could be found.
    """
    imported = None
    dset = conn.getObject("Dataset", ds_id)
    for image in dset.listChildren():
        if image.getName() != label:
            continue

        oldest_allowed_date = datetime.now() - timedelta(seconds=age)
        date = image.getDate()
        if date >= oldest_allowed_date:
            imported = image
            log.success(f"Found imported image: {image.getId()}")
            break

    return imported
