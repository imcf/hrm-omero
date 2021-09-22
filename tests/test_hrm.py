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


def test_parse_config__resources_file():
    """Test the config parser with the supplied HRM config file from 'resources'."""
    infile = "resources/hrm.conf"
    config = hrm.parse_config(infile)
    assert config["OMERO_HOSTNAME"] == "omero.mynetwork.xy"


@patch("builtins.open", new_callable=mock_open, read_data=CONF_SHORT)
def test_parse_config__short(mock_file):
    """Test the config parser with a valid short configuration."""
    config = hrm.parse_config(mock_file)
    assert config["OMERO_HOSTNAME"] == "omero.mynetwork.xy"


@patch("builtins.open", new_callable=mock_open, read_data=CONF_SEMICOLON)
def test_parse_config__semicolon(mock_file):
    """Test the config parser with a single line containing two settings."""
    config = hrm.parse_config(mock_file)
    assert config["FOO"] == "one"
    assert config["BAR"] == "two"


@patch("builtins.open", new_callable=mock_open, read_data=CONF_COMMENT)
def test_parse_config__comment(mock_file):
    """Test the config parser with a line containing a comment after an assignment."""
    config = hrm.parse_config(mock_file)
    assert config["TRIPLE"] == "reloaded"


@patch("builtins.open", new_callable=mock_open, read_data=CONF_NOEQUALS)
def test_parse_config__noequals(mock_file):
    """Test the config parser with a configuration that is missing an assignment."""
    with pytest.raises(SyntaxError):
        hrm.parse_config(mock_file)


@patch("builtins.open", new_callable=mock_open, read_data=CONF_SHORT)
def test_check_config__invalid(mock_file):
    """Test the config checker with a configuration that is missing required entries."""
    config = hrm.parse_config(mock_file)
    with pytest.raises(SyntaxError):
        hrm.check_config(config)


@patch("builtins.open", new_callable=mock_open, read_data=CONF_LONG)
def test_check_config__valid(mock_file):
    """Test the config checker with a valid configuration."""
    config = hrm.parse_config(mock_file)
    assert hrm.check_config(config) is None


def test_job_parameter_summary__valid():
    """Test the parameter summary generator with a valid file from 'resources'."""
    infile = "tests/resources/parameter-summaries/valid-summary.txt"
    summary = hrm.job_parameter_summary(infile)
    # print(summary)
    lines = summary.splitlines()
    # check a line that should contain the converted "μm" unit:
    assert lines[2].startswith("X pixel size (μm)")
    # check another line, we're picking the one with the N/A (line 7)
    assert lines[7] == "Numerical aperture [ch:0]: 2.345"


def test_job_parameter_summary__file_not_found():
    """Test the parameter summary generator with a non-existing file."""
    infile = 't/h/i/s/_/s/h/o/u/l/d/_/n/o/t/_/e/x/i/s/t'
    summary = hrm.job_parameter_summary(infile)
    assert summary is None


def test_parse_summary__valid():
    """Test the parameter summary generator with a valid file from 'resources'."""
    infile = "tests/resources/parameter-summaries/valid-summary.txt"
    summary = hrm.parse_summary(infile)
    # check if we're having an entry containing the converted "μm" unit:
    assert "X pixel size (μm)" in summary["Image Parameters"]
    # check the N/A value for channel 0:
    assert summary["Image Parameters"]["Numerical aperture [ch:0]"] == "2.345"


def test_parse_summary__invalid():
    """Test the summary parser with invalid data containing header duplicates."""
    infile = "tests/resources/parameter-summaries/invalid-summary-duplicate-headers.txt"
    with pytest.raises(KeyError):
        hrm.parse_summary(infile)
    infile = "tests/resources/parameter-summaries/invalid-summary-duplicate-params.txt"
    with pytest.raises(KeyError):
        hrm.parse_summary(infile)


def test_parse_summary__file_not_found():
    """Test the parameter summary generator with a non-existing file."""
    infile = 't/h/i/s/_/s/h/o/u/l/d/_/n/o/t/_/e/x/i/s/t'
    summary = hrm.parse_summary(infile)
    assert summary is None
