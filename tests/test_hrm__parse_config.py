"""Tests for the 'hrm' submodule."""

from unittest.mock import patch, mock_open
import pytest

from hrm_omero import hrm

CONF_SHORT = """
# OMERO_HOSTNAME="omero"
OMERO_HOSTNAME="omero.mynetwork.xy"
# OMERO_HOSTNAME="localhost"
OMERO_PORT="4064"
"""

CONF_LONG = CONF_SHORT + """
# OMERO_PKG specifies the path where the "OMERO.server" package is installed
OMERO_PKG="/opt/OMERO/OMERO.server"
"""

CONF_SEMICOLON = 'FOO="one" ; BAR="two"'

CONF_NOEQUALS = "KEY_WITHOUT_VALUE"

CONF_COMMENT = 'TRIPLE="reloaded"  # whatever that means'


def test_with_example_file():
    """Test the config parser with the example HRM config file from 'resources'."""
    infile = "resources/hrm.conf"
    config = hrm.parse_config(infile)
    assert config["OMERO_HOSTNAME"] == "omero.mynetwork.xy"


@patch("builtins.open", new_callable=mock_open, read_data=CONF_SHORT)
def test_valid_short(mock_file):
    """Test the config parser with a valid short configuration."""
    config = hrm.parse_config(mock_file)
    assert config["OMERO_HOSTNAME"] == "omero.mynetwork.xy"


@patch("builtins.open", new_callable=mock_open, read_data=CONF_SEMICOLON)
def test_valid_with_semicolon(mock_file):
    """Test the config parser with a single line containing two settings."""
    config = hrm.parse_config(mock_file)
    assert config["FOO"] == "one"
    assert config["BAR"] == "two"


@patch("builtins.open", new_callable=mock_open, read_data=CONF_COMMENT)
def test_valid_with_comment(mock_file):
    """Test the config parser with a line containing a comment after an assignment."""
    config = hrm.parse_config(mock_file)
    assert config["TRIPLE"] == "reloaded"


@patch("builtins.open", new_callable=mock_open, read_data=CONF_NOEQUALS)
def test_invalid_no_assignment(mock_file):
    """Test the config parser with a configuration that is missing an assignment."""
    with pytest.raises(SyntaxError):
        hrm.parse_config(mock_file)
