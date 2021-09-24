"""Tests for the `hrm_omero.hrm.parse_summary()` function."""

import os.path

import pytest

from hrm_omero import hrm

BASE_DIR = os.path.join("tests", "resources", "parameter-summaries")
FNAME_VALID = os.path.join(BASE_DIR, "valid-summary.txt")
FNAME_INVALID_HEADERS = os.path.join(BASE_DIR, "invalid-summary-duplicate-headers.txt")
FNAME_INVALID_PARAMS = os.path.join(BASE_DIR, "invalid-summary-duplicate-params.txt")


def test_with_valid_file():
    """Test the summary parser with a valid file from 'resources'."""
    summary = hrm.parse_summary(FNAME_VALID)
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
    infile = 't/h/i/s/_/s/h/o/u/l/d/_/n/o/t/_/e/x/i/s/t'
    summary = hrm.parse_summary(infile)
    assert summary is None
