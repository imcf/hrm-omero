"""Tests for the 'cli.run_task()' function with action 'OMEROtoHRM'.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

import os

import pytest
from hrm_omero import cli

from settings.common import HOSTNAME  # pylint: disable-msg=wrong-import-order


CONF = f'OMERO_HOSTNAME="{HOSTNAME}"'


@pytest.mark.online
def test_download_image(
    monkeypatch, capsys, reach_tcp_or_skip, tmp_path, settings, sha1
):
    """Test the "OMEROtoHRM" action with a valid and accessible image ID.

    Expected behavior is to download the image and the corresponding thumbnail.
    """
    hrm_conf = tmp_path / "hrm.conf"
    with open(hrm_conf, mode="w", encoding="utf-8") as outfile:
        outfile.write(CONF)

    reach_tcp_or_skip(settings.HOSTNAME, settings.PORT)

    # if no password was defined in the settings, check if the environment has one:
    if settings.PASSWORD is not None:
        monkeypatch.setenv("OMERO_PASSWORD", settings.PASSWORD)
    elif "OMERO_PASSWORD" not in os.environ:
        pytest.skip("password for OMERO is required (via settings or environment)")

    download_image = settings.download_image[0]
    dl_fname = download_image["filename"]

    args = ["-vvvv"]
    args.append("--conf")
    args.append(hrm_conf.as_posix())
    args.append("--user")
    args.append(settings.USERNAME)
    args.append("OMEROtoHRM")
    args.append("--imageid")
    args.append(f'G:{download_image["gid"]}:{download_image["image_id"]}')
    args.append("--dest")
    args.append(tmp_path.as_posix())

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
