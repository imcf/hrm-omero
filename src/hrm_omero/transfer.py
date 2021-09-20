"""Transfer related functions."""

import os
import re

from loguru import logger as log

from . import hrm


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

    # TODO I (issue #438): in case the query fails, this means most likely that
    # a file was uploaded in an older version of OMERO and therefore the
    # original file is not available. However, it was possible to upload with
    # the "archive" option, we should check if such archived files are
    # retrieved with the above query.
    # TODO II (issue #398): in case no archived file is available, we could
    # fall back to downloading the OME-TIFF instead.
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

    In case PIL (Python Imaging Library) is installed, download the thumbnail of a given
    OMERO image and place it as preview in the corresponding HRM directory.

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
    try:
        import Image
        import StringIO
    except ImportError:
        return False
    image_obj = conn.getObject("Image", image_id)
    image_data = image_obj.getThumbnail()
    thumbnail = Image.open(StringIO.StringIO(image_data))
    base_dir, fname = os.path.split(dest)
    target = "/hrm_previews/" + fname + ".preview_xy.jpg"
    try:
        thumbnail.save(base_dir + target)
        # TODO: os.chown() to fix permissions, see #457!
        print("Thumbnail downloaded to '%s'." % target)
        return True
    except:  # pylint: disable-msg=bare-except
        print("ERROR downloading thumbnail to '%s'." % target)
        return False


def to_omero(conn, id_str, image_file):
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

    Returns
    -------
    bool
        True in case of success, False otherwise.
    """

    if image_file.lower().endswith((".h5", ".hdf5")):
        print("ERROR: HDF5 files are not supported by OMERO!")
        return False
    # TODO I: group switching required!!
    _, gid, obj_type, dset_id = id_str.split(":")
    if obj_type != "Dataset":
        raise ValueError("A '--dset' ID of the form 'G:7:Dataset:12345' is required!")

    # we have to create the annotations *before* we actually upload the image
    # data itself and link them to the image during the upload - the other way
    # round is not possible right now as the CLI wrapper (see below) doesn't
    # expose the ID of the newly created object in OMERO (confirmed by J-M and
    # Sebastien on the 2015 OME Meeting):
    namespace = "deconvolved.hrm"
    #### mime = 'text/plain'
    # extract the image basename without suffix:
    # TODO: is it [0-9a-f] or really [0-9a-z] as in the original PHP code?
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
    # NOTE: cli._client should be replaced with cli.set_client() when switching
    # to support for OMERO 5.1 and later only:
    cli._client = conn.c  # pylint: disable-msg=protected-access
    import_args = ["import"]

    # disable the upgrade check as it is causing an SSL handshake error and it doesn't
    # make sense in our scenario, see the following forum thread for details:
    # https://forum.image.sc/t/unable-to-use-cli-importer/26424
    import_args.extend(["--skip", "upgrade"])

    # import_args.extend(['--debug', 'ALL'])
    # import_args.extend(['--file', '/tmp/hrm-omero-java-stdout'])
    # import_args.extend(['--errs', '/tmp/hrm-omero-java-stderr'])
    import_args.extend(["-d", dset_id])
    if comment is not None:
        import_args.extend(["--annotation_ns", namespace])
        import_args.extend(["--annotation_text", comment])
    #### for ann_id in annotations:
    ####     import_args.extend(['--annotation_link', str(ann_id)])
    import_args.append(image_file)
    log.debug(f"import_args: {import_args}")
    try:
        cli.invoke(import_args, strict=True)
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
    return True
