"""Tests for the 'cli.main()' and 'cli.run_task() function."""

import re

# from unittest.mock import patch, mock_open
import pytest

from hrm_omero import cli

from .data import RE_HELP


def test_help(capsys):
    """Test main() with ["--help"] being the only parameter.

    Expected behavior is to print the help message to stdout and exit with code 0.
    """
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(["--help"])

    captured = capsys.readouterr()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert re.match(RE_HELP, captured.out)


def test_noaction(capsys):
    """Test main() with no (valid) action selected.

    Expected behavior is to print the help message to stderr and exit with code 2.
    """
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main([])

    captured = capsys.readouterr()
    # print(captured)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
    assert re.match(RE_HELP, captured.err)
