"""Tests for the `hrm_omero.hrm.parse_summary()` function."""

import pytest

from hrm_omero import hrm

from .data import (
    FNAME_VALID,
    FNAME_VALID_WARNING,
    FNAME_VALID_IMAGE,
    FNAME_INVALID_HEADERS,
    FNAME_INVALID_PARAMS,
)


def test_with_valid_file():
    """Test the summary parser with a valid file from 'resources'."""
    summary = hrm.parse_summary(FNAME_VALID)
    # check if we're having an entry containing the converted "μm" unit:
    assert "X pixel size (μm)" in summary["Image Parameters"]
    # check the N/A value for channel 0:
    assert summary["Image Parameters"]["Numerical aperture [ch:0]"] == "2.345"


def test_with_valid_warning_file(caplog):
    """Test parser with a valid file having a 'WARNING' section.

    Such files contain an extra table that does not have a header and are
    simply skipped by the parser while printing a debug level log message.
    """
    summary = hrm.parse_summary(FNAME_VALID_WARNING)
    assert "Skipping table entry that doesn't have a header." in caplog.text
    # check if we're having an entry containing the converted "μm" unit:
    assert "X pixel size (μm)" in summary["Image Parameters"]
    # check the N/A value for channel 0:
    assert summary["Image Parameters"]["Numerical aperture [ch:0]"] == "1.200"


def test_with_valid_image(caplog):
    """Test the summary parser with an *image* file name from 'resources'."""
    summary = hrm.parse_summary(FNAME_VALID_IMAGE)
    assert f"will use it instead of [{FNAME_VALID_IMAGE}]" in caplog.text

    # check if we're having an entry containing the converted "μm" unit:
    assert "X pixel size (μm)" in summary["Image Parameters"]
    # check the N/A value for channel 0:
    assert summary["Image Parameters"]["Numerical aperture [ch:0]"] == "2.345"


def test_with_invalid_file():
    """Test the summary parser with invalid data containing header duplicates."""
    # test with duplicate headers
    with pytest.raises(KeyError):
        hrm.parse_summary(FNAME_INVALID_HEADERS)

    # test with duplicate parameters
    with pytest.raises(KeyError):
        hrm.parse_summary(FNAME_INVALID_PARAMS)


def test_with_non_existing_file():
    """Test the summary parser with a non-existing file."""
    infile = "t/h/i/s/_/s/h/o/u/l/d/_/n/o/t/_/e/x/i/s/t"
    summary = hrm.parse_summary(infile)
    assert summary is None
