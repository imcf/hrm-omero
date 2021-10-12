"""Tests for the 'transfer.fetch_thumbnail() function requiring the '--online' flag.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os
import sys

import pytest
from hrm_omero.transfer import fetch_thumbnail


@pytest.mark.online
def test_thumbnail_dir_unwritable(omero_conn, tmp_path, settings, capsys):
    """Test fetching a thumbnail from OMERO to a location that cannot be written to.

    Expected behavior to return False and print an error.
    """
    print(f"target path for storing thumbnail: {tmp_path}", file=sys.stderr)

    test = settings.download_image[0]

    image_id = test["image_id"]
    dest = tmp_path / "hrm_previews"
    os.mkdir(dest)
    stat = os.stat(dest)
    os.chmod(dest, 0o000)

    image_id = image_id.replace("Image:", "")

    ret = fetch_thumbnail(omero_conn, image_id, dest)
    assert ret is False

    captured = capsys.readouterr()

    assert "ERROR downloading thumbnail" in captured.out

    # make sure the temp dir can be cleaned up again:
    os.chmod(dest, stat.st_mode)
