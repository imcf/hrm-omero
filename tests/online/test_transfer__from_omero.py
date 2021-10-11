"""Tests for the 'transfer.from_omero() function requiring the '--online' flag.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os
import sys

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
        obj_id = f"G:{gid}:Image:{image_id}"

        ret = from_omero(omero_conn, obj_id, tmp_path)
        assert ret is True

        files = os.listdir(tmp_path)
        assert test["filename"] in files

        assert test["sha1sum"] == sha1(tmp_path / test["filename"])

    assert 0
