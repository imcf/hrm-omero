"""Tests for the 'omero.extract_image_id()' function."""

from unittest.mock import mock_open, patch

from hrm_omero.omero import extract_image_id

from .data import IMPORT_YAML_INVALID, IMPORT_YAML_INVALID_MULTI, IMPORT_YAML_VALID


@patch("builtins.open", new_callable=mock_open, read_data=IMPORT_YAML_VALID)
def test_valid_yaml(mock_file, caplog):
    """Test with a valid YAML string.

    Expected behavior is to parse the YAML and return an image ID of type int."""
    ret = extract_image_id(mock_file)
    assert isinstance(ret, int)
    assert ret == 778899
    assert "Successfully parsed Image ID from YAML" in caplog.text


@patch("builtins.open", new_callable=mock_open, read_data=IMPORT_YAML_INVALID)
def test_invalid_yaml(mock_file, caplog):
    """Test with an invalid YAML string.

    Expected behavior is to return `None` and push a message to the log and stdout."""
    ret = extract_image_id(mock_file)
    assert ret is None
    assert "Unexpected YAML retrieved from OMERO" not in caplog.text
    assert "Error parsing imported image ID from YAML output" in caplog.text


@patch("builtins.open", new_callable=mock_open, read_data=IMPORT_YAML_INVALID_MULTI)
def test_invalid_yaml_multi(mock_file, caplog):
    """Test with an invalid YAML string containing multiple Image IDs.

    Expected behavior is to return `None` and push a message to the log and stdout."""
    ret = extract_image_id(mock_file)
    assert ret is None
    assert "Unexpected YAML retrieved from OMERO" in caplog.text
    assert "Error parsing imported image ID from YAML output" in caplog.text
