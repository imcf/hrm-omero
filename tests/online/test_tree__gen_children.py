"""Tests for the 'tree.gen_children()' function

The tests here also require a file `omero_test_settings.py` to be found at the location
where pytest is started from. Look in `tests/resources/settings/` for an example file.
"""

import pytest

from hrm_omero.misc import OmeroId
from hrm_omero.tree import gen_children

# import the settings to test against an actual OMERO instance or skip the whole module
# in case the import fails:
_IMPORT = pytest.importorskip(
    modname="omero_test_settings",
    reason="Couldn't find 'omero_test_settings.py' to import!",
)
SETTINGS = _IMPORT.SETTINGS
GID = SETTINGS["default_group"]


@pytest.mark.online
def test_experimenter_group(omero_conn, caplog):
    """Test by requesting with an 'ExperimenterGroup' omero_id.

    The function is expected to print a warning to the logs and return an empty list.
    """
    omero_id = OmeroId(f"G:{GID}:ExperimenterGroup:{GID}")
    ret = gen_children(omero_conn, omero_id)
    assert ret == []
    assert "trees should be generated via `gen_group_tree()`" in caplog.text
