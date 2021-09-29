"""Tests for the 'cli.run_task() function."""

from hrm_omero import cli


# set the standard arguments for run_task() - note that for several tests we need a
# valid configuration file to reach the relevant parts of the code:
BASE_ARGS = ["--conf", "resources/hrm.conf", "--user", "pytest"]


def test_no_password(capsys, monkeypatch):
    """Test run_task() without specifying a password.

    Expected behavior is to print a message to stderr and return False.
    """
    # make sure the environment has no "OMERO_PASSWORD"
    monkeypatch.delenv("OMERO_PASSWORD", raising=False)

    args = BASE_ARGS.copy()
    args.append("checkCredentials")
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    assert "no password given to connect to OMERO" in captured.err
    assert ret is False


def test_no_action(capsys, monkeypatch):
    """Test run_task() without specifying an action.

    Expected behavior is to print a message to stderr and return False.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    ret = cli.run_task(BASE_ARGS)
    captured = capsys.readouterr()
    assert "No valid action specified that should be performed" in captured.err
    assert ret is False


def test_dry_run_check_credentials(capsys, monkeypatch):
    """Test run_task() with action "checkCredentials" in "dry-run" mode.

    Expected behavior is to print the function name to stdout and return True.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = BASE_ARGS.copy()
    args.append("--dry-run")
    args.append("checkCredentials")
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    assert "dry-run, only showing action and parameters" in captured.out
    assert "function: check_credentials" in captured.out
    assert ret is True


def test_dry_run_retrieve_children(capsys, monkeypatch):
    """Test run_task() with action "retrieveChildren" in "dry-run" mode.

    Expected behavior is to print the function name and args to stdout and return True.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = BASE_ARGS.copy()
    args.append("--dry-run")
    # TODO: order is important, write a failing test where 'action' is the last arg!
    args.append("retrieveChildren")
    args.append("--id")
    args.append("ROOT")
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    print(captured.out)
    assert "dry-run, only showing action and parameters" in captured.out
    assert "function: print_children_json" in captured.out
    assert "{'id_str': 'ROOT'}" in captured.out
    assert ret is True


def test_dry_run_from_omero(capsys, monkeypatch):
    """Test run_task() with action "OMEROtoHRM" in "dry-run" mode.

    Expected behavior is to print the function name and args to stdout and return True.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = BASE_ARGS.copy()
    args.append("--dry-run")
    args.append("OMEROtoHRM")
    args.append("--imageid")
    args.append("G:7:Image:42")
    args.append("--dest")
    args.append("/tmp/foo")
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    print(captured.out)
    assert "dry-run, only showing action and parameters" in captured.out
    assert "function: from_omero" in captured.out
    assert "{'id_str': 'G:7:Image:42', 'dest': '/tmp/foo'}" in captured.out
    assert ret is True


def test_dry_run_to_omero(capsys, monkeypatch):
    """Test run_task() with action "HRMtoOMERO" in "dry-run" mode.

    Expected behavior is to print the function name and args to stdout and return True.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = BASE_ARGS.copy()
    args.append("--dry-run")
    args.append("HRMtoOMERO")
    args.append("--dset")
    args.append("G:7:Dataset:23")
    args.append("--file")
    args.append("/tmp/foo")
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    print(captured.out)
    assert "dry-run, only showing action and parameters" in captured.out
    assert "function: to_omero" in captured.out
    assert "{'id_str': 'G:7:Dataset:23', 'image_file': '/tmp/foo'," in captured.out
    assert ret is True
