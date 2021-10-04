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


def test_init_invalid_group_types(caplog):
    """Test the constructor with invalid group types."""
    with pytest.raises(ValueError):
        OmeroId("X:1:Image:1")
    with pytest.raises(ValueError):
        OmeroId("G:X:Image:1")
    with pytest.raises(ValueError):
        OmeroId("G:1:X:1")
    with pytest.raises(ValueError):
        OmeroId("G:1:Image:X")
