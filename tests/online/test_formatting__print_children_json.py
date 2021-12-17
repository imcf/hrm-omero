"""Tests for the 'formatting.print_children_json()' function

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import pytest
from hrm_omero.formatting import print_children_json
from hrm_omero.misc import OmeroId


@pytest.mark.online
def test_invalid_omero_id(omero_conn, caplog):
    """Test providing an invalid omero_id.

    Expected behavior is to return False and to push a corresponding message to the log.
    """
    omero_id = OmeroId("G:999999:Dataset:999999")
    ret = print_children_json(omero_conn, omero_id)
    assert ret is False
    assert "ERROR generating OMERO tree / node!" in caplog.text
