"""Tests for the 'tree.gen_children()' function

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import pytest

from hrm_omero.misc import OmeroId
from hrm_omero.tree import gen_children


@pytest.mark.online
def test_experimenter_group(omero_conn, caplog, settings):
    """Test by requesting with an 'ExperimenterGroup' omero_id.

    The function is expected to print a warning to the logs and return an empty list.
    """
    omero_id = OmeroId(f"G:{settings.GID}:ExperimenterGroup:{settings.GID}")
    ret = gen_children(omero_conn, omero_id)
    assert ret == []
    assert "trees should be generated via `gen_group_tree()`" in caplog.text
