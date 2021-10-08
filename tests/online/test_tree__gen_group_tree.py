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
def test_tree_structure(omero_conn, caplog, json_is_equal):
    """Check tree structure returned by `gen_group_tree()` with different inputs.

    Expected behavior is to log a corresponding message and to generate the tree for the
    requested group.
    """
    for values in SETTINGS["gen_group_tree"]:
        caplog.clear()
        group = values["group"]
        received = gen_group_tree(omero_conn, group=group)
        assert received is not None
        if group is None:
            assert "Getting group from current context" in caplog.text
        else:
            assert "Getting group from current context" not in caplog.text

        expected = values["tree"]
        assert json_is_equal(expected, received)

