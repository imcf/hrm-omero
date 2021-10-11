"""Tests for the 'formatting.print_children_json()' function

The tests here also require a file `omero_test_settings.py` to be found at the location
where pytest is started from. Look in `tests/resources/settings/` for an example file.
"""

import pytest

from hrm_omero.misc import OmeroId
from hrm_omero.formatting import print_children_json


@pytest.mark.online
def test_invalid_omero_id(omero_conn, caplog):
    """Test providing an invalid omero_id.

    Expected behavior is to return False and to push a corresponding message to the log.
    """
    omero_id = OmeroId("G:-100:Dataset:-100")
    ret = print_children_json(omero_conn, omero_id)
    assert ret is False
    assert "ERROR generating OMERO tree / node!" in caplog.text
