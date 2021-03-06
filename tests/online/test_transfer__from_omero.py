"""Tests for the 'transfer.from_omero() function requiring the '--online' flag.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os
import sys
from pathlib import Path

import pytest
from hrm_omero.transfer import from_omero


def _download_image(conn, dl_settings, tmp_path, sha1):
    """Trigger the download of an image object and test the result(s).

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        An OMERO connection object.
    dl_settings : dict
        A dict with the details of the image to be downloaded and checked, e.g.
        ```
        {
            "gid": 8,
            "image_id": "Image:16",
            "sha1sums": [
                ("48ee0def0bbaf96a306604d38dccdd", "2ch-mi-xd.ics"),
                ("f96a306aaaa0def0bbaccdd604d38d", "2ch-mi-xd.ids"),
            ],
        }
        ```
    tmp_path : pathlib.PosixPath
        A temporary path object to store the downloaded file(s).
    sha1 : function
        A function calculating the SHA-1 sum of a file.
    """
    gid = dl_settings["gid"]
    image_id = dl_settings["image_id"]
    if "," in image_id:
        image_id = image_id.split(",")[0]
        print(f"Using only first ID for requesting the download: {image_id}")
    sha1sums = dl_settings["sha1sums"]
    tmp_path.mkdir(exist_ok=True)  # make sure the target path exists

    obj_id = f"G:{gid}:{image_id}"
    print(f"obj_id: [{obj_id}]")

    ret = from_omero(conn, obj_id, tmp_path)
    assert ret is True

    files = [str(f.relative_to(tmp_path)) for f in tmp_path.glob("**/*")]
    for (expected_sha1, filename) in sha1sums:
        assert filename in files
        assert expected_sha1 == sha1(tmp_path / filename)
        print(f"{filename}: {expected_sha1}")


@pytest.mark.online
def test_download_image(omero_conn, tmp_path, sha1, settings):
    """Test downloading a known image from OMERO and check its properties.

    Expected behavior is to store the image with its original filename.
    """
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)

    for test in settings.download_image:
        _download_image(omero_conn, test, tmp_path, sha1)


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
    sha1sum = test["sha1sums"][0][0]
    fname = test["sha1sums"][0][1]
    target_file = tmp_path / fname
    obj_id = f"G:{gid}:{image_id}"

    ret = from_omero(omero_conn, obj_id, tmp_path / "some-other-filename")
    assert ret is True

    files = os.listdir(tmp_path)
    assert fname in files

    assert sha1sum == sha1(target_file)


@pytest.mark.online
def test_download_file_exists(omero_conn, tmp_path, settings, capsys):
    """Test downloading an image from OMERO that already exists in the target path.

    Expected behavior to return False and print an error.
    """
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)

    test = settings.download_image[0]

    gid = test["gid"]
    image_id = test["image_id"]
    fname = test["sha1sums"][0][1]
    target_file = tmp_path / fname

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
    id_str = "G:999999:Image:999999"
    ret = from_omero(omero_conn, id_str, tmp_path)
    assert ret is False


@pytest.mark.online
def test_download_image_other_group(omero_conn, tmp_path, sha1, settings):
    """Test downloading a known image that does NOT belong to the default group.

    Expected behavior is to store the image with its original filename.
    """
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)

    for test in settings.download_image_other_group:
        _download_image(omero_conn, test, tmp_path, sha1)


@pytest.mark.online
def test_download_images_various_groups(omero_conn, tmp_path, sha1, settings):
    """Test downloading multiple images from different groups.

    This tests whether group switching for multiple subsequent downloads works
    as expected by first fetching one or more images from the user's default
    group, then from another group and finally again from the default group.
    """
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)

    dl_settings = (
        settings.download_image
        + settings.download_image_other_group
        + settings.download_image
    )

    for i, test in enumerate(dl_settings):
        _download_image(omero_conn, test, tmp_path / str(i), sha1)


@pytest.mark.online
def test_download_multifile_datasets(omero_conn, tmp_path, sha1, settings):
    """Download datasets consisting of multiple files in a given structure."""
    print(f"target path for downloading: {tmp_path}", file=sys.stderr)
    for dataset in settings.SITE_SPECIFIC["MULTI_FILE_DATASETS"]:
        check_pairs = []
        with open(dataset["SHA1SUMS"], "r", encoding="utf-8") as sha1sums:
            for line in sha1sums:
                sha1_expected = line[:40]
                filename = line[42:].rstrip("\n")
                check_pairs.append((sha1_expected, filename))

        dl_settings = {
            "gid": dataset["GID"],
            "image_id": dataset["IID"],
            "sha1sums": check_pairs,
        }
        print(f"dl_settings: {dl_settings}")
        _download_image(omero_conn, dl_settings, tmp_path, sha1)
