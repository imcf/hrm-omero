"""Transfer related functions."""

import os
import re
import tempfile
from io import BytesIO

from loguru import logger as log
from PIL import Image

from . import hrm
from .omero import extract_image_id


def from_omero(conn, id_str, dest):
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
    id_str : str
        The ID of the OMERO image (e.g. `G:23:Image:42`).
    dest : str
        The destination path.

    Returns
    -------
    bool
        True in case the download was successful, False otherwise.
    """
    _, gid, obj_type, image_id = id_str.split(":")
    if obj_type != "Image":
        raise ValueError("An '--imageid' ID of the form 'G:7:Image:98765' is required!")

    if not image_id:
        print("Couldn't parse ID '%s'. Expecting [GID]:[Type]:[Image_ID]" % id_str)
        return False

    # Provided that the tree displays only groups that the current user has access to,
    # cross-group query (introduced in OMERO 4.4) is a generic way to get the image.
    if not gid:
        gid = "-1"
    conn.SERVICE_OPTS.setOmeroGroup(gid)
    # another way for switching the group was suggested in HRM upstream ticket #539:
    # conn.setGroupForSession(gid)

    # check if dest is a directory, rewrite it otherwise:
    if not os.path.isdir(dest):
        dest = os.path.dirname(dest)
    from omero_model_OriginalFileI import OriginalFileI

    # use image objects and getFileset() methods to determine original files,
    # see the following OME forum thread for some more details:
    # https://www.openmicroscopy.org/community/viewtopic.php?f=6&t=7563
    image_obj = conn.getObject("Image", image_id)
    if not image_obj:
        print("ERROR: can't find image with ID %s!" % image_id)
        return False

    fset = image_obj.getFileset()
    if not fset:
        print("ERROR: no original file(s) for image %s found!" % image_id)
        return False

    # NOTE: the idea of offering to download the OME-TIFF from OMERO (i.e. the converted
    # data) as an alternative has been discarded for the moment - see upstream HRM
    # ticket #398 (http://hrm.svi.nl:8080/redmine/issues/398)
    downloads = []
    # assemble a list of items to download, check if any files already exist:
    for fset_file in fset.listFiles():
        tgt = os.path.join(dest, fset_file.getName())
        if os.path.exists(tgt):
            print("ERROR: target file '%s' already existing!" % tgt)
            return False

        fset_id = fset_file.getId()
        downloads.append((fset_id, tgt))
    # now initiate the downloads for all original files:
    for (fset_id, tgt) in downloads:
        try:
            conn.c.download(OriginalFileI(fset_id), tgt)
        except:  # pylint: disable-msg=bare-except
            print("ERROR: downloading %s to '%s' failed!" % (fset_id, tgt))
            return False

        print("ID %s downloaded as '%s'" % (fset_id, os.path.basename(tgt)))
    # NOTE: for filesets with a single file or e.g. ICS/IDS pairs it makes
    # sense to use the target name of the first file to construct the name for
    # the thumbnail, but it is unclear whether this is a universal approach:
    fetch_thumbnail(conn, image_id, downloads[0][1])
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
    image_obj = conn.getObject("Image", image_id)
    image_data = image_obj.getThumbnail()
    thumbnail = Image.open(BytesIO(image_data))
    base_dir, fname = os.path.split(dest)
    target = "/hrm_previews/" + fname + ".preview_xy.jpg"
    try:
        thumbnail.save(base_dir + target)
        # TODO: os.chown() to fix permissions, see #457!
        msg = f"Thumbnail downloaded to '{target}'."
        print(msg)
        log.success(msg)
        return True
    except Exception as err:  # pylint: disable-msg=broad-except
        msg = f"ERROR downloading thumbnail to '{target}': {err}"
        print(msg)
        log.error(msg)
        return False


def to_omero(conn, id_str, image_file, omero_logfile=""):
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
        print(msg)
        raise TypeError(msg)

    _, gid, obj_type, dset_id = id_str.split(":")
    if obj_type != "Dataset":
        raise ValueError("A '--dset' ID of the form 'G:7:Dataset:12345' is required!")

    # set the group for this import session:
    conn.setGroupForSession(gid)

    # we have to create the annotations *before* we actually upload the image
    # data itself and link them to the image during the upload - the other way
    # round is not possible right now as the CLI wrapper (see below) doesn't
    # expose the ID of the newly created object in OMERO (confirmed by J-M and
    # Sebastien on the 2015 OME Meeting):
    namespace = "deconvolved.hrm"
    #### mime = 'text/plain'
    # extract the image basename without suffix:
    # NOTE: HRM job IDs are generated via PHP's `uniqid()` call that is giving a
    # 13-digit hexadecimal string (8 digits UNIX time and 5 digits microsconds)
    basename = re.sub(r"(_[0-9a-f]{13}_hrm)\..*", r"\1", image_file)
    comment = hrm.job_parameter_summary(basename + ".parameters.txt")
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

    if comment is not None:
        import_args.extend(["--annotation_ns", namespace])
        import_args.extend(["--annotation_text", comment])
    #### for ann_id in annotations:
    ####     import_args.extend(['--annotation_link', str(ann_id)])
    import_args.append(image_file)
    log.debug(f"import_args: {import_args}")
    try:
        cli.invoke(import_args, strict=True)
        imported_id = extract_image_id(cap_stdout)
        log.success(f"Imported OMERO image ID: {imported_id}")
    except Exception as err:  # pylint: disable-msg=broad-except
        msg = f"ERROR: uploading '{image_file}' to {id_str} failed!"
        print(msg)
        log.error(msg)
        msg = f"OMERO error message: >>>{err}<<<"
        print(msg)
        log.error(msg)
        msg = f"import_args: {import_args}"
        print(msg)
        log.warning(msg)
        return False
    finally:
        tempdir.cleanup()

    return True
