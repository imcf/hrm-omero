"""Tests for the 'tree.gen_group_tree()' function

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import pytest
from hrm_omero.tree import gen_group_tree


@pytest.mark.online
def test_tree_structure(omero_conn, caplog, json_is_equal, settings):
    """Check tree structure returned by `gen_group_tree()` with different inputs.

    Expected behavior is to log a corresponding message and to generate the tree for the
    requested group.
    """
    for values in settings.gen_group_tree:
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


@pytest.mark.online
def test_tree_structure_invalid_group(omero_conn, caplog):
    """Check `gen_group_tree()` with an invalid group being requested.

    Expected behavior is to log a corresponding message and to generate the tree for the
    requested group.
    """
    with pytest.raises(RuntimeError):
        gen_group_tree(omero_conn, group=-100)

    assert "Unable to identify group with ID" in caplog.text
