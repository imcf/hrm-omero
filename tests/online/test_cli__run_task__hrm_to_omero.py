"""Tests for the 'cli.run_task()' function with action 'HRMtoOMERO'.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os

import pytest
from hrm_omero import cli

from settings.common import HOSTNAME  # pylint: disable-msg=wrong-import-order

CONF = f'OMERO_HOSTNAME="{HOSTNAME}"'


def build_args(hrm_conf, tmp_path, settings, additional_args):
    args = [
        "-vvvv",
        "--conf",
        hrm_conf(tmp_path, CONF),
        "--user",
        settings.USERNAME,
        "HRMtoOMERO",
    ]

    return args + additional_args


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip")
def test_unsupported_formats(hrm_conf, tmp_path, settings, capsys):
    """Test attempting imports with unsupported file name suffixes.

    Expected behavior is to return False and print an error message.
    """
    additional_args = [
        "--dset",
        settings.import_image[0]["target_id"],
        "--file",
        settings.import_image[0]["filename"] + ".h5",
    ]
    args = build_args(hrm_conf, tmp_path, settings, additional_args)
    print(args)

    ret = cli.run_task(args)
    assert ret is False

    captured = capsys.readouterr()
    assert "format not supported by OMERO" in captured.out
