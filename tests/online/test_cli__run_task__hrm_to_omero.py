"""Tests for the 'cli.run_task()' function with action 'HRMtoOMERO'.

These tests require `site_specific.py` to be found in `tests/online/settings`, see
`tests/resources/settings/` for a template.
"""

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


def _import_image(import_image, hrm_conf, user, expected_stdout, cli_args, capfd):
    """Test the "HRMtoOMERO" action with a valid local file.

    Expected behavior is to import the file, and to print a bunch of specific
    messages to stderr.
    """
    fname = import_image["filename"]
    target_id = import_image["target_id"]
    args = cli_args(
        "HRMtoOMERO",
        hrm_conf=hrm_conf,
        user=user,
        action_args=[
            "--dset",
            target_id,
            "--file",
            fname,
        ],
    )

    ret = cli.run_task(args)
    assert ret is True

    captured = capfd.readouterr().err
    # print(f"import stdout: {captured.out}")
    # print(f"import stderr: {captured.err}")

    for pattern in expected_stdout:
        assert pattern in captured


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip")
def test_upload_image(capfd, tmp_path, settings, hrm_conf, cli_args):
    """Call `_import_image()` for each defined import test setting."""
    for import_image in settings.import_image:
        _import_image(
            import_image,
            hrm_conf=hrm_conf(tmp_path, CONF),
            user=settings.USERNAME,
            expected_stdout=settings.import_messages,
            cli_args=cli_args,
            capfd=capfd,
        )


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip", "req_cache")
def test_omerouserdir_writable(tmp_path, settings, hrm_conf, cli_args, monkeypatch):
    """Run a fake import with the $OMERO_USERDIR environment variable being set.

    This will affect omero-py's internal behavior of where to look for the
    extracted `OMERO.java.zip` package and download a fresh one in case it can't
    find one in `$OMERO_USERDIR/cache/jars/`.

    Expected behavior is actually a side-effect of the `import` call as it will
    attempt to download the described ZIP file and create the folder hierarchy
    from it. So the call to `run_task()` is expected to return `False` (as we
    are not importing an actual file) but the temporary location used in the
    test is expected to contain the related OMERO jar files after.
    """
    import_image = settings.import_image[0]
    target_id = import_image["target_id"]
    args = cli_args(
        "HRMtoOMERO",
        hrm_conf=hrm_conf(tmp_path, CONF),
        user=settings.USERNAME,
        action_args=[
            "--dset",
            target_id,
            "--file",
            "fname",
        ],
    )
    monkeypatch.setenv("OMERO_USERDIR", tmp_path.as_posix())

    cache_path = tmp_path / "cache" / "jars"
    assert cache_path.exists() is False

    ret = cli.run_task(args)
    assert ret is False

    assert cache_path.exists() is True

    omero_java_dir = list(cache_path.glob("OMERO.java-*-ice*"))
    assert len(omero_java_dir) == 1
    omero_java_files = (omero_java_dir[0] / "libs").glob("*")
    # version 5.6.3 contains 189 files, let's just check if there are many:
    assert len(list(omero_java_files)) > 150


@pytest.mark.online
@pytest.mark.usefixtures("omeropw", "reach_tcp_or_skip", "req_cache")
def test_omerouserdir_nonwritable(
    tmp_path, settings, hrm_conf, cli_args, monkeypatch, capsys
):
    """Test with $OMERO_USERDIR set to a non-writable location.

    Expected behavior is that the call to `omero.cli.CLI.invoke` will attempt to
    download "OMERO.java.zip" to the non-writable location and therefore fail
    with a "Permission denied" error raising a `PermissionError`.
    """
    conf_path = tmp_path / "conf"
    omero_userdir = tmp_path / "omero_userdir"
    import_image = settings.import_image[0]
    fname = tmp_path / "non-existing-file"
    target_id = import_image["target_id"]

    # create directories required below:
    omero_userdir.mkdir()
    conf_path.mkdir()
    assert omero_userdir.exists()
    assert conf_path.exists()

    args = cli_args(
        "HRMtoOMERO",
        hrm_conf=hrm_conf(conf_path, CONF),
        user=settings.USERNAME,
        action_args=[
            "--dset",
            target_id,
            "--file",
            "fname",
        ],
    )

    # make sure the file doesn't exist as we don't want to trigger an actual import:
    assert fname.exists() is False

    try:
        # remove all permissions from tmp_dir but remember them for later:
        stat = omero_userdir.stat()
        omero_userdir.chmod(0o000)

        monkeypatch.setenv("OMERO_USERDIR", omero_userdir.as_posix())

        ret = cli.run_task(args)
        assert ret is False
    finally:
        # make sure the temp dir can be cleaned up again:
        omero_userdir.chmod(stat.st_mode)

    captured = capsys.readouterr()
    assert "Permission denied" in captured.err
    assert "documentation about the 'OMERO_USERDIR'" in captured.err
