"""Tests for the 'omero.add_annotation_keyvalue() function requiring the '--online' flag.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import pytest
from hrm_omero.omero import add_annotation_keyvalue


@pytest.mark.online
def test_invalid_target(omero_conn, caplog):
    """Test with a non-existing target ID.

    Expected behavior is to return False and log a warning.
    """
    id_str = "G:-1:Image:-1"
    print(id_str)
    ret = add_annotation_keyvalue(omero_conn, id_str, None)
    assert ret is False

    assert "Unable to identify target object" in caplog.text
