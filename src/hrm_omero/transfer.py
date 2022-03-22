"""Transfer related functions."""

import os
import tempfile
from io import BytesIO
from pathlib import Path
import stat

from loguru import logger as log
from PIL import Image

from . import hrm
from .decorators import connect_and_set_group
from .omero import extract_image_id, add_annotation_keyvalue
from .misc import printlog, changemodes


@connect_and_set_group
def from_omero(conn, omero_id, dest):
    """Download the corresponding original file(s) from an image ID.

    This only works for image IDs that were created with OMERO 5.0 or later as previous
    versions don't have an "original file" linked to an image.

    Note that files will be downloaded with their original name, which is not
    necessarily the name shown by OMERO, e.g. if an image name was changed in OMERO. To
    keep filesets consistent, we have to preserve the original names!

    In addition to the original file(s), it also downloads a thumbnail of the requested
    file from OMERO and puts it into the appropriate place so HRM will show it as a
    preview until the user hits "re-generate preview".

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    omero_id : hrm_omero.misc.OmeroId
        The ID of the OMERO image to be downloaded.
    dest : str
        The destination path.

    Returns
    -------
    bool
        True in case the download was successful, False otherwise.

    Raises
    ------
    ValueError
        Raised in case an object that is not of type `Image` was requested.
    """
    log.trace(f"Downloading {omero_id.obj_type}:{omero_id.obj_id} to [{dest}]...")

    # conn.setGroupForSession(-1)
    conn.SERVICE_OPTS.setOmeroGroup(-1)  # still working with OMERO-5.6.3
    if omero_id.obj_type != "Image":
        raise ValueError("Currently only the download of 'Image' objects is supported!")

    # check if dest is a directory, rewrite it otherwise:
    if not os.path.isdir(dest):
        # FIXME: this should raise a ValueError as it's quite counter-intuitive that
        # specifying a file *name* for the target doesn't have an effect on how the
        # downloaded file will be called actually!
        dest = os.path.dirname(dest)
    from omero_model_OriginalFileI import OriginalFileI

    # use image objects and getFileset() methods to determine original files,
    # see the following OME forum thread for some more details:
    # https://www.openmicroscopy.org/community/viewtopic.php?f=6&t=7563
    target_obj = conn.getObject(omero_id.obj_type, omero_id.obj_id)
    if not target_obj:
        printlog("ERROR", f"ERROR: can't find image with ID [{omero_id.obj_id}]!")
        return False

    fset = target_obj.getFileset()
    if not fset:  # pragma: no cover
        printlog("ERROR", f"ERROR: no original file(s) for [{omero_id.obj_id}] found!")
        return False

    # NOTE: the idea of offering to download the OME-TIFF from OMERO (i.e. the converted
    # data) as an alternative has been discarded for the moment - see upstream HRM
    # ticket #398 (http://hrm.svi.nl:8080/redmine/issues/398)
    downloads = []
    # assemble a list of items to download
    for fset_file in fset.listFiles():
        # for foo in dir(fset_file):
        #     log.error(foo)
        file_name = fset_file.getName()
        file_path = fset_file.getPath()
        downloads.append((fset_file.getId(), os.path.join(file_path, file_name)))

    # determine the common prefix, e.g. `hrm-test-02_3/2022-02/17/14-34-16.480/`
    all_files = [x[1] for x in downloads]
    strip = os.path.commonprefix(all_files).rindex("/") + 1

    # strip the common prefix, check if any of the files already exist:
    top_level = []
    for i, pair in enumerate(downloads):
        rel_path = pair[1][strip:]
        log.trace(f"relative path: {rel_path}")
        top_level.append(rel_path.split("/")[0])
        abs_path = os.path.join(dest, rel_path)
        downloads[i] = (pair[0], abs_path)
        if os.path.exists(abs_path):
            printlog("ERROR", f"ERROR: file '{abs_path}' already existing!")
            return False

    # now initiate the downloads for all original files:
    for (file_id, tgt) in downloads:
        try:
            log.trace(f"Downloading original file [{file_id}] to [{tgt}]...")
            os.makedirs(os.path.dirname(tgt), exist_ok=True)
            conn.c.download(OriginalFileI(file_id), tgt)
        except Exception as err:  # pylint: disable-msg=broad-except
            printlog("ERROR", f"ERROR: downloading {file_id} to '{tgt}' failed: {err}")
            return False
        printlog("SUCCESS", f"ID {file_id} downloaded as '{os.path.basename(tgt)}'")

    changemodes(dest, top_level)

    # NOTE: for filesets with a single file or e.g. ICS/IDS pairs it makes
    # sense to use the target name of the first file to construct the name for
    # the thumbnail, but it is unclear whether this is a universal approach:
    fetch_thumbnail(conn, omero_id.obj_id, downloads[0][1])
    return True


def fetch_thumbnail(conn, image_id, dest):
    """Download the thumbnail of a given image from OMERO.

    OMERO provides thumbnails for stored images, this function downloads the thumbnail
    image and places it as preview in the corresponding HRM directory.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    image_id : str
        An OMERO object ID of an image (e.g. '102').
    dest : str
        The destination filename.

    Returns
    -------
    bool
        True in case the download was successful, False otherwise.
    """
    log.info(f"Trying to fetch thumbnail for OMERO image [{image_id}]...")
    log.trace(f"Requested target location: [{dest}].")

    base_dir, fname = os.path.split(dest)
    target_dir = Path(base_dir) / "hrm_previews"
    target = Path(target_dir) / f"{fname}.preview_xy.jpg"

    image_obj = conn.getObject("Image", image_id)
    image_data = image_obj.getThumbnail()
    log.trace(f"len(image_data)={len(image_data)}")
    thumbnail = Image.open(BytesIO(image_data))
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        # TODO: consider using `misc.changemodes()`
        # for an unkown reason using mode=(S_IRWXU | S_IRWXG) on the `mkdir()` call
        # doesn't seem to work, so we have to add group-write in a second step:
        target_dir.chmod(target_dir.stat().st_mode | stat.S_IWGRP)
        thumbnail.save(target.as_posix(), format="jpeg")
        printlog("SUCCESS", f"Thumbnail downloaded to '{target}'.")
        target.chmod(target.stat().st_mode | stat.S_IWGRP)
        log.success(f"Added group-write permissions to '{target}'.")
    except Exception as err:  # pylint: disable-msg=broad-except
        printlog("ERROR", f"ERROR downloading thumbnail to '{target}': {err}")
        return False

    return True


def to_omero(conn, id_str, image_file, omero_logfile="", _fetch_zip_only=False):
    """Upload an image into a specific dataset in OMERO.

    In case we know from the suffix that a given  format is not supported by OMERO, the
    upload will not be initiated at all (e.g. for SVI-HDF5, having the suffix '.h5').

    The import itself is done by instantiating the CLI class, assembling the required
    arguments, and finally running `cli.invoke()`. This eventually triggers the
    `importer()` method defined in [OMERO's Python bindings][1].

    [1]: https://github.com/ome/omero-py/blob/master/src/omero/plugins/import.py

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    id_str : str
        The ID of the target dataset in OMERO (e.g. `G:7:Dataset:23`).
    image_file : str
        The local image file including the full path.
    omero_logfile : str, optional
        The prefix of files to be used to capture OMERO's `import` call stderr messages.
        If the parameter is non-empty the `--debug ALL` option will be added to the
        `omero` call with the output being placed in the specified file. If the
        parameter is omitted or empty, debug messages will be disabled.
    _fetch_zip_only : bool, optional
        Replaces all parameters to the import call by `--advanced-help`, which is
        **intended for INTERNAL TESTING ONLY**. No actual import will be attempted!

    Returns
    -------
    bool
        True in case of success, False otherwise.

    Raises
    ------
    TypeError
        Raised in case `image_file` is in a format that is not supported by OMERO.
    ValueError
        Raised in case `id_str` has an invalid format.
    """

    # TODO: revisit this, as e.g. BDV .h5 files are supported for now!
    if image_file.lower().endswith((".h5", ".hdf5")):
        msg = f"ERROR importing [{image_file}]: HDF5 format not supported by OMERO!"
        printlog("ERROR", msg)
        raise TypeError(msg)

    _, gid, obj_type, dset_id = id_str.split(":")
    if obj_type != "Dataset":
        msg = "Currently only the upload to 'Dataset' objects is supported!"
        printlog("ERROR", msg)
        raise ValueError(msg)

    # set the group for this import session:
    conn.setGroupForSession(gid)

    # we have to create the annotations *before* we actually upload the image
    # data itself and link them to the image during the upload - the other way
    # round is not possible right now as the CLI wrapper (see below) doesn't
    # expose the ID of the newly created object in OMERO (confirmed by J-M and
    # Sebastien on the 2015 OME Meeting):
    #### namespace = "deconvolved.hrm"
    #### mime = 'text/plain'
    #### annotations = []
    #### # TODO: the list of suffixes should not be hardcoded here!
    #### for suffix in ['.hgsb', '.log.txt', '.parameters.txt']:
    ####     if not os.path.exists(basename + suffix):
    ####         continue
    ####     ann = conn.createFileAnnfromLocalFile(
    ####         basename + suffix, mimetype=mime, ns=namespace, desc=None)
    ####     annotations.append(ann.getId())

    # currently there is no direct "Python way" to import data into OMERO, so we have to
    # use the CLI wrapper for this...
    # TODO: check the more recent code mentioned by the OME developers in the forum
    # thread: https://forum.image.sc/t/automated-uploader-to-omero-in-python/38290
    # https://gitlab.com/openmicroscopy/incubator/omero-python-importer/-/blob/master/import.py)
    # and also see https://pypi.org/project/omero-upload/
    from omero.cli import CLI

    cli = CLI()
    cli.loadplugins()
    cli.set_client(conn.c)
    import_args = ["import"]

    # disable upgrade checks (https://forum.image.sc/t/unable-to-use-cli-importer/26424)
    import_args.extend(["--skip", "upgrade"])

    if omero_logfile:
        log.warning(f"Messages (stderr) from import will go to [{omero_logfile}].")
        import_args.extend(["--debug", "ALL"])
        import_args.extend(["--errs", omero_logfile])

    import_args.extend(["-d", dset_id])

    # capture stdout and request YAML format to parse the output later on:
    tempdir = tempfile.TemporaryDirectory(prefix="hrm-omero__")
    cap_stdout = f"{tempdir.name}/omero-import-stdout"
    log.debug(f"Capturing stdout of the 'omero' call into [{cap_stdout}]...")
    import_args.extend(["--file", cap_stdout])
    import_args.extend(["--output", "yaml"])

    #### for ann_id in annotations:
    ####     import_args.extend(['--annotation_link', str(ann_id)])
    import_args.append(image_file)
    if _fetch_zip_only:
        # calling 'import --advanced-help' will trigger the download of OMERO.java.zip
        # in case it is not yet present (the extract_image_id() call will then fail,
        # resulting in the whole function returning "False")
        printlog("WARNING", "As '_fetch_zip_only' is set NO IMPORT WILL BE ATTEMPTED!")
        import_args = ["import", "--advanced-help"]
    log.debug(f"import_args: {import_args}")
    try:
        cli.invoke(import_args, strict=True)
        imported_id = extract_image_id(cap_stdout)
        log.success(f"Imported OMERO image ID: {imported_id}")
    except PermissionError as err:
        printlog("ERROR", err)
        omero_userdir = os.environ.get("OMERO_USERDIR", "<not-set>")
        printlog("ERROR", f"Current OMERO_USERDIR value: {omero_userdir}")
        printlog(
            "ERROR",
            (
                "Please make sure to read the documentation about the 'OMERO_USERDIR' "
                "environment variable and also check if the file to be imported has "
                "appropriate permissions!"
            ),
        )
        return False
    except Exception as err:  # pylint: disable-msg=broad-except
        printlog("ERROR", f"ERROR: uploading '{image_file}' to {id_str} failed!")
        printlog("ERROR", f"OMERO error message: >>>{err}<<<")
        printlog("WARNING", f"import_args: {import_args}")
        return False
    finally:
        tempdir.cleanup()

    target_id = f"G:{gid}:Image:{imported_id}"
    try:
        summary = hrm.parse_summary(image_file)
        add_annotation_keyvalue(conn, target_id, summary)
    except Exception as err:  # pragma: no cover # pylint: disable-msg=broad-except
        log.error(f"Creating a parameter summary from [{image_file}] failed: {err}")

    return True
