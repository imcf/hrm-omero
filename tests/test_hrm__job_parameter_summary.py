"""Tests for the `hrm_omero.hrm.job_parameter_summary()` function."""

from hrm_omero import hrm


def test_with_valid_file():
    """Test the parameter summary generator with a valid file from 'resources'."""
    infile = "tests/resources/parameter-summaries/valid-summary.txt"
    summary = hrm.job_parameter_summary(infile)
    # print(summary)
    lines = summary.splitlines()
    # check a line that should contain the converted "μm" unit:
    assert lines[2].startswith("X pixel size (μm)")
    # check another line, we're picking the one with the N/A (line 7)
    assert lines[7] == "Numerical aperture [ch:0]: 2.345"


def test_with_non_existing_file():
    """Test the parameter summary generator with a non-existing file."""
    infile = 't/h/i/s/_/s/h/o/u/l/d/_/n/o/t/_/e/x/i/s/t'
    summary = hrm.job_parameter_summary(infile)
    assert summary is None
