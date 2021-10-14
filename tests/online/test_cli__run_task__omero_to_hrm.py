"""Tests for the 'cli.run_task()' function with action 'OMEROtoHRM'.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os

import pytest
from hrm_omero import cli

from settings.common import HOSTNAME  # pylint: disable-msg=wrong-import-order

CONF = f'OMERO_HOSTNAME="{HOSTNAME}"'
ACTION = "OMEROtoHRM"


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip")
def test_download_image(capsys, tmp_path, settings, sha1, hrm_conf, cli_args):
    """Test the "OMEROtoHRM" action with a valid and accessible image ID.

    Expected behavior is to download the image and the corresponding thumbnail.
    """
    download_image = settings.download_image[0]
    dl_fname = download_image["filename"]

    args = cli_args(
        action=ACTION,
        action_args=[
            "--imageid",
            f'G:{download_image["gid"]}:{download_image["image_id"]}',
            "--dest",
            tmp_path.as_posix(),
        ],
        hrm_conf=hrm_conf(tmp_path, CONF),
        user=settings.USERNAME,
    )

    ret = cli.run_task(args)
    assert ret is True

    image_file = (tmp_path / dl_fname).as_posix()
    preview_file = (tmp_path / "hrm_previews" / f"{dl_fname}.preview_xy.jpg").as_posix()

    for check_file in [image_file, preview_file]:
        assert os.path.exists(check_file)
        assert os.stat(check_file).st_size > 0

    assert sha1(image_file) == download_image["sha1sum"]

    captured = capsys.readouterr()
    assert "downloaded as" in captured.out
    assert "Thumbnail downloaded to" in captured.out
