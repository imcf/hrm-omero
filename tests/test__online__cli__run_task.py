"""Tests for the 'cli.run_task() function requiring the '--online' flag.

Those tests (usually) also require a file `omero_test_settings.py` to be found at the
location where pytest is started from. Look in `tests/resources/settings/` for an
example file.
"""

from unittest.mock import patch, mock_open
import pytest

from hrm_omero import cli


# import the settings to test against an actual OMERO instance or skip the whole module
# in case the import fails:
_IMPORT = pytest.importorskip(
    modname="omero_test_settings",
    reason="Couldn't find 'omero_test_settings.py' to import!",
)
SETTINGS = _IMPORT.SETTINGS
CONF = f'OMERO_HOSTNAME="{SETTINGS["hostname"]}"'
USERNAME = SETTINGS["username"]

# set the standard arguments for run_task():
BASE_ARGS = ["-vvvv", "--conf", "config_file_will_be_mocked"]


@pytest.mark.online
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_valid_login(mock_file, capsys, monkeypatch):
    """Test the "checkCredentials" action.

    Expected behavior is to print sucess to stdout and a few infos to the log (stderr).
    """
    assert mock_file  # we don't need the mock file for an actual call...

    # if no password is given, the $OMERO_PASSWORD environment variable will be used:
    if "password" in SETTINGS:
        monkeypatch.setenv("OMERO_PASSWORD", SETTINGS["password"])

    args = BASE_ARGS.copy()
    args.append("--user")
    args.append(USERNAME)
    args.append("checkCredentials")

    ret = cli.run_task(args)

    captured = capsys.readouterr()
    assert "Connected to OMERO" in captured.out
    assert f"New OMERO connection [user={USERNAME}]" in captured.err
    assert "The user's default group is" in captured.err
    assert f"Closed OMERO connection [user={USERNAME}]" in captured.err
    assert ret is True


@pytest.mark.online
@patch("builtins.open", new_callable=mock_open, read_data=CONF)
def test_retrieve_children_root(mock_file, capsys, monkeypatch):
    """Test the "retrieveChildren" action requesting the `ROOT` tree.

    Expected behavior is to print an OMERO tree in JSON notation.
    """
    assert mock_file  # we don't need the mock file for an actual call...

    # if no password is given, the $OMERO_PASSWORD environment variable will be used:
    if "password" in SETTINGS:
        monkeypatch.setenv("OMERO_PASSWORD", SETTINGS["password"])

    args = BASE_ARGS.copy()
    args.append("--user")
    args.append(USERNAME)
    args.append("retrieveChildren")
    args.append("--id")
    args.append("ROOT")

    ret = cli.run_task(args)

    captured = capsys.readouterr()
    # TODO: evaluate printed JSON properly, for now we're just checking a few things:
    assert 'children": [' in captured.out
    assert 'ExperimenterGroup:' in captured.out
    assert '"owner":' in captured.out
    assert f"Closed OMERO connection [user={USERNAME}]" in captured.err
    assert ret is True


# TODO: test invalid username / password
