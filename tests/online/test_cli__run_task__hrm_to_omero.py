"""Tests for the 'cli.run_task()' function with action 'HRMtoOMERO'.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os

import pytest
from hrm_omero import cli

from settings.common import HOSTNAME  # pylint: disable-msg=wrong-import-order

CONF = f'OMERO_HOSTNAME="{HOSTNAME}"'


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip")
def test_unsupported_formats(hrm_conf, tmp_path, settings, capsys, cli_args):
    """Test attempting imports with unsupported file name suffixes.

    Expected behavior is to return False and print an error message.
    """
    args = cli_args(
        "HRMtoOMERO",
        [
            "--dset",
            settings.import_image[0]["target_id"],
            "--file",
            settings.import_image[0]["filename"] + ".h5",
        ],
        hrm_conf(tmp_path, CONF),
        settings.USERNAME,
    )

    ret = cli.run_task(args)
    assert ret is False

    captured = capsys.readouterr()
    assert "format not supported by OMERO" in captured.out


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip")
def test_unsupported_target(hrm_conf, tmp_path, settings, capsys, cli_args):
    """Test attempting imports to an invalid target (only "Dataset" is allowed).

    Expected behavior is to return False and print an error message.
    """
    args = cli_args(
        "HRMtoOMERO",
        [
            "--dset",
            "G:7:Project:42",
            "--file",
            settings.import_image[0]["filename"],
        ],
        hrm_conf(tmp_path, CONF),
        settings.USERNAME,
    )

    ret = cli.run_task(args)
    assert ret is False

    captured = capsys.readouterr()
    print(captured.out)
    assert "only the upload to 'Dataset' objects is supported" in captured.out
