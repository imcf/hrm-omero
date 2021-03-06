"""Tests for the package's __init__ file."""

from hrm_omero import __version__


def test_version():
    """Ensure we're running against the expected package version."""
    assert __version__ == "1.0.0-dev0"
