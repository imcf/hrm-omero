"""Tests for the `hrm_omero.hrm.parse_summary()` function."""

import pytest

from hrm_omero import hrm


def test_with_valid_file():
    """Test the parameter summary generator with a valid file from 'resources'."""
    infile = "tests/resources/parameter-summaries/valid-summary.txt"
    summary = hrm.parse_summary(infile)
    # check if we're having an entry containing the converted "μm" unit:
    assert "X pixel size (μm)" in summary["Image Parameters"]
    # check the N/A value for channel 0:
    assert summary["Image Parameters"]["Numerical aperture [ch:0]"] == "2.345"


def test_with_invalid_file():
    """Test the summary parser with invalid data containing header duplicates."""
    infile = "tests/resources/parameter-summaries/invalid-summary-duplicate-headers.txt"
    with pytest.raises(KeyError):
        hrm.parse_summary(infile)
    infile = "tests/resources/parameter-summaries/invalid-summary-duplicate-params.txt"
    with pytest.raises(KeyError):
        hrm.parse_summary(infile)


def test_with_non_existing_file():
    """Test the parameter summary generator with a non-existing file."""
    infile = 't/h/i/s/_/s/h/o/u/l/d/_/n/o/t/_/e/x/i/s/t'
    summary = hrm.parse_summary(infile)
    assert summary is None
