"""Tests for the 'cli.run_task() function with action 'checkCredentials'.

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
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_valid_login(mock_file, capsys, omeropw, reach_tcp_or_skip, settings):
    """Test the "checkCredentials" action.

    Expected behavior is to print sucess to stdout and a few infos to the log (stderr).
    """
    assert mock_file  # we don't need the mock file for an actual call...

    args = BASE_ARGS.copy()
    args.append("--user")
    args.append(settings.USERNAME)
    args.append("checkCredentials")

    ret = cli.run_task(args)
    assert ret is True

    captured = capsys.readouterr()
    print(captured.err)
    assert f"Connected to OMERO [user={settings.USERNAME}, " in captured.out
    assert "User's default group is" in captured.err
    assert f"Closed OMERO connection [user={settings.USERNAME}]" in captured.err


@pytest.mark.online
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_invalid_password(mock_file, capsys, monkeypatch, reach_tcp_or_skip, settings):
    """Test the "checkCredentials" action with an invalid password.

    Expected behavior is to return False and print an error message to stdout.
    """
    assert mock_file  # we don't need the mock file for an actual call...

    monkeypatch.setenv("OMERO_PASSWORD", "nobody-will-ever-use-this-pw-in-omero-really")

    args = BASE_ARGS.copy()
    args.append("--user")
    args.append(settings.USERNAME)
    args.append("checkCredentials")

    ret = cli.run_task(args)
    assert ret is False

    captured = capsys.readouterr()
    print(captured.err)
    assert "ERROR logging into OMERO" in captured.out
