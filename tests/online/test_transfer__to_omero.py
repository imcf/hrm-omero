"""Tests for the 'transfer.to_omero()' function requiring the '--online' flag.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os

import pytest
from hrm_omero.omero import find_recently_imported
from hrm_omero.transfer import to_omero


@pytest.mark.online
def test_unsupported_formats(omero_conn, settings):
    """Test attempting imports with unsupported file name suffixes.

    Expected behavior is to raise a TypeError.
    """
    import_image = settings.import_image[0]
    id_str = import_image["target_id"]
    for suffix in [".h5", ".hdf5"]:
        image_file = import_image["filename"] + suffix
        print(f"Trying with filename [{image_file}]...")
        with pytest.raises(TypeError, match="format not supported by OMERO"):
            to_omero(omero_conn, id_str, image_file)


@pytest.mark.online
def test_unsupported_target(omero_conn, settings):
    """Test attempting imports to an invalid target (only "Dataset" is allowed).

    Expected behavior is to raise a ValueError.
    """
    import_image = settings.import_image[0]
    fname = import_image["filename"]
    sha1sum = import_image["sha1sum"]
    target_id = "G:7:Project:42"

    print(f"Trying to import [{fname}] into [{target_id}] (sha1: {sha1sum})")
    with pytest.raises(ValueError, match="only the upload to 'Dataset' objects"):
        to_omero(omero_conn, target_id, fname)


@pytest.mark.online
def test_import_image(omero_conn, settings, capfd):
    """Test importing local files into OMERO and check its properties in OMERO.

    Expected behavior is to import the file, and to print a bunch of specific messages
    to stderr. The test tries to find back the imported object in OMERO and checks if
    the size and fileset count matches the ones defined in the test settings.
    """
    expected_output_patterns = [
        "Using import target: Dataset",
        "FILESET_UPLOAD_PREPARATION",
        "FILESET_UPLOAD_START",
        "FILE_UPLOAD_STARTED",
        "FILE_UPLOAD_COMPLETE",
        "IMPORT_STARTED",
        "PIXELDATA_PROCESSED",
        "IMPORT_DONE",
    ]
    for import_image in settings.import_image:
        fname = import_image["filename"]
        sha1sum = import_image["sha1sum"]
        target_id = import_image["target_id"]

        print(f"Trying to import [{fname}] into [{target_id}] (sha1: {sha1sum})")
        ret = to_omero(omero_conn, target_id, fname)
        assert ret is True

        # capsys won't work as it misses the output of subprocesses (the "omero import"
        # call in this case), but using capfd does the job:
        captured = capfd.readouterr()
        for pattern in expected_output_patterns:
            assert pattern in captured.err

        ds_id = target_id.split(":")[-1]
        imported = find_recently_imported(omero_conn, ds_id, os.path.basename(fname))
        assert imported is not None

        files_info = imported.getImportedFilesInfo()
        assert files_info["count"] == import_image["fset_count"]
        assert files_info["size"] == import_image["fset_size"]


@pytest.mark.online
def test_invalid_target(omero_conn, settings, capfd):
    """Test attempting an import to a dataset that can't be written to.

    Expected behavior is to return False and log an error.

    TODO: check what happens if an existing dataset is given, but in a group where the
    user doesn't have permissions!
    """
    expected_output_patterns = [
        "Error on import",
        "ome.formats.importer.ImportLibrary - Exiting on error",
    ]
    import_image = settings.import_image[0]
    fname = import_image["filename"]
    sha1sum = import_image["sha1sum"]
    target_id = "G:-1:Dataset:-1"

    print(f"Trying to import [{fname}] into [{target_id}] (sha1: {sha1sum})")
    ret = to_omero(omero_conn, target_id, fname)
    assert ret is False

    # capsys won't work as it misses the output of subprocesses (the "omero import"
    # call in this case), but using capfd does the job:
    captured = capfd.readouterr()
    for pattern in expected_output_patterns:
        assert pattern in captured.err
