"""Tests for the 'tree.gen_group_tree()' function

The tests here also require a file `omero_test_settings.py` to be found at the location
where pytest is started from. Look in `tests/resources/settings/` for an example file.
"""

import pytest

from hrm_omero.tree import gen_group_tree

# import the settings to test against an actual OMERO instance or skip the whole module
# in case the import fails:
_IMPORT = pytest.importorskip(
    modname="omero_test_settings",
    reason="Couldn't find 'omero_test_settings.py' to import!",
)
SETTINGS = _IMPORT.SETTINGS


@pytest.mark.online
def test_group_is_none(omero_conn, caplog, json_is_equal):
    """Test calling the function with `group` set to `None`.

    Expected behavior is to log a corresponding message and to generate the tree for the
    user's default group.
    """
    received = gen_group_tree(omero_conn, group=None)
    assert received is not None
    assert "Getting group from current context" in caplog.text

    expected = SETTINGS["gen_group_tree__none"]
    assert json_is_equal(expected, received)
