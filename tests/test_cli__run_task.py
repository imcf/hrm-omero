"""Tests for the 'cli.run_task() function."""

import pytest

from hrm_omero import cli


def test_no_password(capsys, monkeypatch, cli_args):
    """Test run_task() without specifying a password.

    Expected behavior is to print a message to stderr and return False.
    """
    # make sure the environment has no "OMERO_PASSWORD"
    monkeypatch.delenv("OMERO_PASSWORD", raising=False)

    args = cli_args("checkCredentials")
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    assert "no password given to connect to OMERO" in captured.err
    assert ret is False


def test_no_action(capsys, monkeypatch, cli_args):
    """Test run_task() without specifying an action.

    Expected behavior is to print a message to stderr and return False.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = cli_args("NoAction")
    args.pop(-1)  # remove the "NoAction" argument
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    assert "No valid action specified that should be performed" in captured.err
    assert ret is False


def test_dry_run_check_credentials(capsys, monkeypatch, cli_args):
    """Test run_task() with action "checkCredentials" in "dry-run" mode.

    Expected behavior is to print the function name to stdout and return True.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = cli_args("checkCredentials", dry_run=True)
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    assert "dry-run, only showing action and parameters" in captured.out
    assert "function: check_credentials" in captured.out
    assert ret is True


def test_dry_run_retrieve_children(capsys, monkeypatch, cli_args):
    """Test run_task() with action "retrieveChildren" in "dry-run" mode.

    Expected behavior is to print the function name and args to stdout and return True.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = cli_args("retrieveChildren", ["--id", "ROOT"], dry_run=True)
    ret = cli.run_task(args)
    captured = capsys.readouterr()
    print(captured.out)
    assert "dry-run, only showing action and parameters" in captured.out
    assert "function: print_children_json" in captured.out
    assert "omero_id: [ROOT]" in captured.out
    assert ret is True


def test_dry_run_from_omero(capsys, monkeypatch, cli_args):
    """Test run_task() with action "OMEROtoHRM" in "dry-run" mode.

    Expected behavior is to print the function name and args to stdout and return True.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = cli_args(
        "OMEROtoHRM",
        [
            "--imageid",
            "G:7:Image:42",
            "--dest",
            "/tmp/foo",
        ],
        dry_run=True,
    )

    ret = cli.run_task(args)
    captured = capsys.readouterr()
    print(captured.out)
    assert "dry-run, only showing action and parameters" in captured.out
    assert "function: from_omero" in captured.out
    assert "omero_id: [G:7:Image:42]" in captured.out
    assert "dest: [/tmp/foo]" in captured.out
    assert ret is True


def test_dry_run_to_omero(capsys, monkeypatch, cli_args):
    """Test run_task() with action "HRMtoOMERO" in "dry-run" mode.

    Expected behavior is to print the function name and args to stdout and return True.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    args = cli_args(
        "HRMtoOMERO",
        [
            "--dset",
            "G:7:Dataset:23",
            "--file",
            "/tmp/foo",
        ],
        dry_run=True,
    )

    ret = cli.run_task(args)
    captured = capsys.readouterr()
    print(captured.out)
    assert "dry-run, only showing action and parameters" in captured.out
    assert "function: to_omero" in captured.out
    assert "omero_id: [G:7:Dataset:23]" in captured.out
    assert "image_file: [/tmp/foo]" in captured.out
    assert ret is True


def test_wrong_parameter_order(capsys, monkeypatch, cli_args):
    """Test run_task() with a wrong order of the otherwise correct parameters.

    Expected behavior is to print an error message and raise a SystemExit.
    """
    monkeypatch.setenv("OMERO_PASSWORD", "non_empty_dummy_password_string")

    # the order is important here, trying to supply the action ("retrieveChildren") as
    # the last parameter will result in an error (as the "--id" parameter belongs to the
    # sub-parser that is only selected when the corresponding action keyword is found)
    args = cli_args("retrieveChildren", ["--id", "ROOT"], dry_run=True)
    args.append(args.pop(-3))  # swap 3rd last element to the last position

    with pytest.raises(SystemExit):
        cli.run_task(args)
    captured = capsys.readouterr()
    print(captured.err)
    assert "error: argument action: invalid choice" in captured.err
