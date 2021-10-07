"""Tests for the 'hrm' submodule."""

from unittest.mock import mock_open, patch

import pytest
from hrm_omero import hrm

from .data import CONF_LONG, CONF_SHORT


@patch("builtins.open", new_callable=mock_open, read_data=CONF_SHORT)
def test_invalid_missing_entries(mock_file):
    """Test the config checker with a configuration that is missing required entries."""
    config = hrm.parse_config(mock_file)
    with pytest.raises(SyntaxError):
        hrm.check_config(config)


@patch("builtins.open", new_callable=mock_open, read_data=CONF_LONG)
def test_valid(mock_file):
    """Test the config checker with a valid configuration."""
    config = hrm.parse_config(mock_file)
    assert hrm.check_config(config) is None
