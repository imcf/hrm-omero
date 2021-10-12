"""Tests for the 'transfer.from_omero() function requiring the '--online' flag.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os
import sys
from pathlib import Path

import pytest
from hrm_omero.transfer import from_omero


@pytest.mark.online
def test_download_image(omero_conn, tmp_path, sha1, settings):
    """Test downloading a known image from OMERO and check its properties.

    Expected behavior is to store the image with its original filename.
    """
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)

    for test in settings.download_image:
        gid = test["gid"]
        image_id = test["image_id"]
        target_file = tmp_path / test["filename"]
        obj_id = f"G:{gid}:{image_id}"
        print(f"obj_id: [{obj_id}]")

        ret = from_omero(omero_conn, obj_id, tmp_path)
        assert ret is True

        files = os.listdir(tmp_path)
        assert test["filename"] in files

        assert test["sha1sum"] == sha1(target_file)


@pytest.mark.online
def test_download_image_filename(omero_conn, tmp_path, sha1, settings):
    """Test downloading a known image from OMERO to a full path.

    Expected behavior is that it will be stored under its original name, not the one
    specified in the call until the corresponding code will be adapted to raise a
    ValueError instead.
    """
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)

    test = settings.download_image[0]

    gid = test["gid"]
    image_id = test["image_id"]
    target_file = tmp_path / test["filename"]
    obj_id = f"G:{gid}:{image_id}"

    ret = from_omero(omero_conn, obj_id, tmp_path / "some-other-filename")
    assert ret is True

    files = os.listdir(tmp_path)
    assert test["filename"] in files

    assert test["sha1sum"] == sha1(target_file)


@pytest.mark.online
def test_download_file_exists(omero_conn, tmp_path, settings, capsys):
    """Test downloading an image from OMERO that already exists in the target path.

    Expected behavior to return False and print an error.
    """
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)

    test = settings.download_image[0]

    gid = test["gid"]
    image_id = test["image_id"]
    target_file = tmp_path / test["filename"]

    obj_id = f"G:{gid}:{image_id}"

    Path(target_file).touch()

    ret = from_omero(omero_conn, obj_id, tmp_path)
    assert ret is False

    captured = capsys.readouterr()

    assert "already existing" in captured.out


@pytest.mark.online
def test_download_dir_unwritable(omero_conn, tmp_path, settings, capsys):
    """Test downloading an image from OMERO to a location that cannot be written to.

    Expected behavior to return False and print an error.
    """
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)

    test = settings.download_image[0]

    gid = test["gid"]
    image_id = test["image_id"]
    stat = os.stat(tmp_path)
    os.chmod(tmp_path, 0o000)

    obj_id = f"G:{gid}:{image_id}"

    ret = from_omero(omero_conn, obj_id, tmp_path)
    assert ret is False

    captured = capsys.readouterr()

    assert "ERROR: downloading" in captured.out

    # make sure the temp dir can be cleaned up again:
    os.chmod(tmp_path, stat.st_mode)


@pytest.mark.online
def test_download_dataset(omero_conn, tmp_path):
    """Test downloading a dataset (currently unsupported).

    Expected behavior is to raise a ValueError.
    """
    id_str = "G:1:Dataset:1"
    with pytest.raises(ValueError, match="only the download of 'Image' objects"):
        from_omero(omero_conn, id_str, tmp_path)


@pytest.mark.online
def test_download_nonexisting(omero_conn, tmp_path):
    """Test requesting an image that doesn't exist.

    Expected behavior is to return False.
    """
    id_str = "G:1:Image:-1"
    ret = from_omero(omero_conn, id_str, tmp_path)
    assert ret is False
