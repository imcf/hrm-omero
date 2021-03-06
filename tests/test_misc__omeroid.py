"""Tests for the 'misc.OmeroId' class."""

import pytest

from hrm_omero.misc import OmeroId


def test_init_valid_object_types(caplog):
    """Test the constructor with all defined valid object types."""
    valid_id_strings = [
        "G:1:Image:1",
        "G:1:Dataset:1",
        "G:1:Project:1",
        "G:1:Experimenter:1",
        "G:1:ExperimenterGroup:1",
    ]
    for id_str in valid_id_strings:
        caplog.clear()
        assert str(OmeroId(id_str)) == id_str
        assert "Validated ID string" in caplog.text

    caplog.clear()
    assert str(OmeroId("ROOT")) == "G:-1:BaseTree:-1"
    assert "Converted special ID 'ROOT' to" in caplog.text


def test_init_invalid_id_strings():
    """Test the constructor with invalid ID strings."""
    with pytest.raises(ValueError) as exc_info:
        OmeroId("X:1:Image:1")
    assert "Invalid group qualifier" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        OmeroId("G:X:Image:1")
    assert "invalid literal for int" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        OmeroId("G:1:X:1")
    assert "Invalid object type" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        OmeroId("G:1:Image:X")
    assert "invalid literal for int" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        OmeroId("G:1:Image:-1")
    assert "Invalid object ID" in str(exc_info.value)
