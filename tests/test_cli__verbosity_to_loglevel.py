"""Tests for the 'cli.verbosity_to_loglevel()' function."""

import pytest

from hrm_omero import cli


def test_loglevel():
    """Test the verbosity_to_loglevel() function."""
    assert cli.verbosity_to_loglevel(0) == "WARNING"
    assert cli.verbosity_to_loglevel(1) == "SUCCESS"
    assert cli.verbosity_to_loglevel(2) == "INFO"
    assert cli.verbosity_to_loglevel(3) == "DEBUG"
    assert cli.verbosity_to_loglevel(4) == "TRACE"
    assert cli.verbosity_to_loglevel(7) == "TRACE"

    with pytest.raises(TypeError):
        cli.verbosity_to_loglevel(None)

    with pytest.raises(TypeError):
        cli.verbosity_to_loglevel("level-string")
