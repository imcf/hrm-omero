"""Tests for the 'cli.bool_to_exitstatus()' function."""

from hrm_omero import cli


def test_bool_to_exitstatus():
    """Test the bool_to_exitstatus() function."""
    assert cli.bool_to_exitstatus(True) == 0
    assert cli.bool_to_exitstatus(False) == 1
    assert cli.bool_to_exitstatus(-1) == -1
    assert cli.bool_to_exitstatus(0) == 0
    assert cli.bool_to_exitstatus(1) == 1
    assert cli.bool_to_exitstatus(2) == 2
    assert cli.bool_to_exitstatus("foo") == "foo"
