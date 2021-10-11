"""Tests for the 'cli.run_task() function requiring the '--online' flag.

The tests here also require a file `omero_test_settings.py` to be found at the location
where pytest is started from. Look in `tests/resources/settings/` for an example file.
"""

import os
from unittest.mock import mock_open, patch

import pytest
from hrm_omero import cli
from settings.common import HOSTNAME

CONF = f'OMERO_HOSTNAME="{HOSTNAME}"'

# set the standard arguments for run_task():
BASE_ARGS = ["-vvvv", "--conf", "config_file_will_be_mocked"]


@pytest.mark.online
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_valid_login(mock_file, capsys, monkeypatch, reach_tcp_or_skip, settings):
    """Test the "checkCredentials" action.

    Expected behavior is to print sucess to stdout and a few infos to the log (stderr).
    """
    reach_tcp_or_skip(settings.HOSTNAME, settings.PORT)

    assert mock_file  # we don't need the mock file for an actual call...

    # if no password was defined in the settings, check if the environment has one:
    if settings.PASSWORD is not None:
        monkeypatch.setenv("OMERO_PASSWORD", settings.PASSWORD)
    elif "OMERO_PASSWORD" not in os.environ:
        pytest.skip("password for OMERO is required (via settings or environment)")

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
    reach_tcp_or_skip(settings.HOSTNAME, settings.PORT)

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


@pytest.mark.online
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_retrieve_children_root(
    mock_file, capsys, monkeypatch, reach_tcp_or_skip, settings
):
    """Test the "retrieveChildren" action requesting the `ROOT` tree.

    Expected behavior is to print an OMERO tree in JSON notation.
    """
    reach_tcp_or_skip(settings.HOSTNAME, settings.PORT)

    assert mock_file  # we don't need the mock file for an actual call...

    # if no password was defined in the settings, check if the environment has one:
    if settings.PASSWORD is not None:
        monkeypatch.setenv("OMERO_PASSWORD", settings.PASSWORD)
    elif "OMERO_PASSWORD" not in os.environ:
        pytest.skip("password for OMERO is required (via settings or environment)")

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
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_retrieve_children_many(
    mock_file, capsys, monkeypatch, json_is_equal, reach_tcp_or_skip, settings
):
    """Test "retrieveChildren" requesting various items as defined in test settings.

    Expected behavior is to print the defined OMERO trees, they are required to match
    the `json_result` attribute from the corresponding test settings dict.

    Example
    -------
    >>> SETTINGS = {
    ...     "retrieveChildren": [
    ...         {
    ...             "omero_id": "G:2354:Experimenter:9",
    ...             "json_result": '''
    ...                 [
    ...                     {
    ...                         "children": [],
    ...                         "class": "Project",
    ...                         "id": "G:2354:Project:8404",
    ...                         "label": "HRM Demo Data",
    ...                         "load_on_demand": true,
    ...                         "owner": "hrm-omero-testuser"
    ...                     }
    ...                 ]
    ...             '''
    ...         }
    ...     ]
    ... }
    """
    reach_tcp_or_skip(settings.HOSTNAME, settings.PORT)

    assert mock_file  # we don't need the mock file for an actual call...

    # if no password was defined in the settings, check if the environment has one:
    if settings.PASSWORD is not None:
        monkeypatch.setenv("OMERO_PASSWORD", settings.PASSWORD)
    elif "OMERO_PASSWORD" not in os.environ:
        pytest.skip("password for OMERO is required (via settings or environment)")

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
