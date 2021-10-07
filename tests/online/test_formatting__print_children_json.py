"""Tests for the 'formatting.print_children_json()' function

The tests here also require a file `omero_test_settings.py` to be found at the location
where pytest is started from. Look in `tests/resources/settings/` for an example file.
"""

import pytest

from hrm_omero.misc import OmeroId
from hrm_omero.formatting import print_children_json

# import the settings to test against an actual OMERO instance or skip the whole module
# in case the import fails:
_IMPORT = pytest.importorskip(
    modname="omero_test_settings",
    reason="Couldn't find 'omero_test_settings.py' to import!",
)
SETTINGS = _IMPORT.SETTINGS
CONF = f'OMERO_HOSTNAME="{SETTINGS["hostname"]}"'


@pytest.mark.online
def test_invalid_omero_id(omero_conn, caplog):
    """Test providing an invalid omero_id.

    Expected behavior is FIXME
    """
    omero_id = OmeroId("G:-100:ExperimenterGroup:-100")
    ret = print_children_json(omero_conn, omero_id)
    assert ret is False
    assert "ERROR generating OMERO tree / node!" in caplog.text
