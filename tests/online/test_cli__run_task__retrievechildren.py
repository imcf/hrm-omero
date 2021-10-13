"""Tests for the 'cli.run_task() function with action 'retrieveChildren'.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

from unittest.mock import mock_open, patch

import pytest
from hrm_omero import cli

from settings.common import HOSTNAME  # pylint: disable-msg=wrong-import-order

CONF = f'OMERO_HOSTNAME="{HOSTNAME}"'

# set the standard arguments for run_task():
BASE_ARGS = ["-vvvv", "--conf", "config_file_will_be_mocked"]


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip")
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_retrieve_children_root(mock_file, capsys, settings):
    """Test the "retrieveChildren" action requesting the `ROOT` tree.

    Expected behavior is to print an OMERO tree in JSON notation.
    """
    assert mock_file  # we don't need the mock file for an actual call...

    args = BASE_ARGS.copy()
    args.append("--user")
    args.append(settings.USERNAME)
    args.append("retrieveChildren")
    args.append("--id")
    args.append("ROOT")

    ret = cli.run_task(args)
    assert ret is True

    captured = capsys.readouterr()
    # TODO: evaluate printed JSON properly, for now we're just checking a few things:
    assert 'children": [' in captured.out
    assert "ExperimenterGroup:" in captured.out
    assert '"owner":' in captured.out
    assert f"Closed OMERO connection [user={settings.USERNAME}]" in captured.err


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip")
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_retrieve_children_many(mock_file, capsys, json_is_equal, settings):
    """Test "retrieveChildren" requesting various items as defined in test settings.

    Expected behavior is to print the defined OMERO trees, they are required to match
    the `json_result` attribute from the corresponding test settings dict.
    """
    assert mock_file  # we don't need the mock file for an actual call...

    for current_config in settings.retrieveChildren:
        omero_id = current_config["omero_id"]

        args = BASE_ARGS.copy()
        args.append("--user")
        args.append(settings.USERNAME)
        args.append("retrieveChildren")
        args.append("--id")
        args.append(omero_id)

        ret = cli.run_task(args)
        assert ret is True

        captured = capsys.readouterr()

        assert json_is_equal(current_config["json_result"], captured.out)
