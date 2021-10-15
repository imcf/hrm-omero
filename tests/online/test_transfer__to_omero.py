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


def _test_import_image(conn, import_image, capfd, expected_stdout, logfile=""):
    """Test importing local files into OMERO and check its properties in OMERO.

    Expected behavior is to import the file, and to print a bunch of specific messages
    to stderr. The test tries to find back the imported object in OMERO and checks if
    the size and fileset count matches the ones defined in the test settings.
    """
    fname = import_image["filename"]
    sha1sum = import_image["sha1sum"]
    target_id = import_image["target_id"]

    print(f"Trying to import [{fname}] into [{target_id}] (sha1: {sha1sum})")
    ret = to_omero(conn, target_id, fname, logfile)
    assert ret is True

    # capsys won't work as it misses the output of subprocesses (the "omero import"
    # call in this case), but using capfd does the job:
    captured = capfd.readouterr().err
    # print(f"import stdout: {captured.out}")
    # print(f"import stderr: {captured.err}")
    if logfile:
        with open(logfile, "r", encoding="utf-8") as infile:
            captured = infile.read()

    for pattern in expected_stdout:
        assert pattern in captured

    ds_id = target_id.split(":")[-1]
    imported = find_recently_imported(conn, ds_id, os.path.basename(fname))
    assert imported is not None

    files_info = imported.getImportedFilesInfo()
    assert files_info["count"] == import_image["fset_count"]
    assert files_info["size"] == import_image["fset_size"]


@pytest.mark.online
def test_import_image(omero_conn, settings, capfd):
    """Call `_test_import_image()` for each defined import test setting."""
    for import_image in settings.import_image:
        _test_import_image(omero_conn, import_image, capfd, settings.import_messages)


@pytest.mark.online
def test_import_image_log(omero_conn, settings, capfd, tmp_path):
    """Call `_test_import_image()` for one import setting using a log file."""
    import_image = settings.import_image[0]
    logfile = str(tmp_path / "omero-import-debug-log")
    _test_import_image(
        omero_conn, import_image, capfd, settings.import_messages, logfile
    )


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


@pytest.mark.online
@pytest.mark.usefixtures("req_cache")
def test_omerouserdir_writable(omero_conn, settings, monkeypatch, tmp_path):
    """Call `to_omero()` with env variable `OMERO_USERDIR` set.

    With the environment variable set to a writable location the expected
    behavior is to download and extract "OMERO.java.zip" into a folder under
    `cache/jars/` inside that location.

    The call to `transfer.to_omero()` has the `_fetch_zip_only` flag set so it
    will return False and the only side-effect expected is the creation of the
    described hierarchy with the files extracted from the ZIP.
    """
    import_image = settings.import_image[0]
    target_id = import_image["target_id"]

    monkeypatch.setenv("OMERO_USERDIR", tmp_path.as_posix())
    cache_path = tmp_path / "cache" / "jars"
    assert cache_path.exists() is False

    ret = to_omero(omero_conn, target_id, "//", _fetch_zip_only=True)
    assert ret is False

    assert cache_path.exists() is True

    omero_java_dir = list(cache_path.glob("OMERO.java-*-ice*"))
    assert len(omero_java_dir) == 1
    omero_java_files = (omero_java_dir[0] / "libs").glob("*")
    # version 5.6.3 contains 189 files, let's just check if there are many:
    assert len(list(omero_java_files)) > 150


@pytest.mark.online
@pytest.mark.usefixtures("req_cache")
def test_omerouserdir_nonwritable(omero_conn, settings, monkeypatch, tmp_path, caplog):
    """Call `to_omero()` with `OMERO_USERDIR` set to a non-writable location.

    Expected behavior is that the call to `omero.cli.CLI.invoke` will attempt to
    download "OMERO.java.zip" to the non-writable location and therefore fail
    with a "Permission denied" error raising a `PermissionError`.
    """
    import_image = settings.import_image[0]
    fname = tmp_path / "non-existing-file"
    target_id = import_image["target_id"]

    # make sure the file doesn't exist as we don't want to trigger an actual import:
    assert fname.exists() is False

    # remove all permissions from tmp_dir but remember them for later:
    stat = tmp_path.stat()
    tmp_path.chmod(0o000)

    monkeypatch.setenv("OMERO_USERDIR", tmp_path.as_posix())

    ret = to_omero(omero_conn, target_id, fname.as_posix())
    assert ret is False

    # make sure the temp dir can be cleaned up again:
    tmp_path.chmod(stat.st_mode)

    assert "Permission denied" in caplog.text
    assert "documentation about the 'OMERO_USERDIR'" in caplog.text
