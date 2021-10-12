"""Tests for the 'omero.find_recently_imported() function requiring the '--online' flag.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import pytest
from hrm_omero.omero import find_recently_imported


@pytest.mark.online
def test_no_image_found(omero_conn, settings):
    """Test with a non-existing image.

    Expected behavior is to return None.
    """
    ds_id = settings.import_image[0]["target_id"].split(":")[-1]
    print(ds_id)
    label = "this is not expected to exist as a label for an image"
    ret = find_recently_imported(omero_conn, ds_id, label, age=-600)
    assert ret is None
