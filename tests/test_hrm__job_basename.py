"""Tests for the `hrm_omero.hrm.parse_job_basename()` function."""

from hrm_omero import hrm


def test_hrm_resultfile_label():
    """Test the parser with a string looking like an HRM-generated label.

    The tested string is matching the regexp for HRM-style labels, so the result should
    have the dot and suffix parts removed.
    """
    base = "210924-cells-live05"
    jobid = "0123456789abc_hrm"
    suffix = "ics"
    parsed = hrm.parse_job_basename(f"{base}_{jobid}.{suffix}")
    assert parsed == f"{base}_{jobid}"


def test_non_hrm_like_label():
    """Test the parser with a string that doesn't contain an HRM-style part.

    The tested the string doesn't match the regexp for HRM-labels, so the result is
    expected to identical to the input.
    """
    base = "deconvolved_01"
    suffix = "tif"
    to_parse = f"{base}.{suffix}"
    parsed = hrm.parse_job_basename(to_parse)
    assert parsed == to_parse
