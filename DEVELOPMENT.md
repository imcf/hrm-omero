# Developing the HRM-OMERO connector

## Using poetry

The project is using [poetry][d1] for packaging and dependency management. To set up a
development environment use this command, it will set up a fresh *virtual environment*
with the correct dependencies and install the project in ***editable*** mode:

```bash
git clone https://github.com/imcf/hrm-omero
cd hrm-omero
poetry install
```

## Installing a pre-release from TestPyPI

To make dependency resolution work with the test repository a command like this can be
used:

```bash
pip install \
    -i https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    hrm-omero==0.4.0.dev1
```

## Updating local `dev` wheels

One common scenario is to work on the source tree using your local Desktop and manually
testing interaction with the HRM's web interface in a container by (repeatedly) creating
wheel packages through poetry and pip-installing them inside the container.

However, when installing a wheel with the same version (e.g. `0.4.0-dev7`) multiple
times subsequently, pip's `--force` option has to be used. Unfortunately this will also
try to re-build the `Ice` wheel from scratch which is quite a time-consuming process. To
avoid this, you can simply use the locally cached `Ice` wheel and supply it along the
command to "force-reinstall" the `hrm-omero` wheel, e.g. like this:

```bash
# find the previously built and cached Ice wheel:
ICE_WHEEL=$(find .cache/pip/wheels/ | grep -i ice)
# move it out of the cache to preserve it and have a shorter path:
mv -v "$ICE_WHEEL" .

# use 'pip' to install the new hrm-omero wheel while using the previous Ice:
/opt/venvs/hrm-omero/bin/pip install \
    --upgrade \
    --force \
    hrm_omero-0.4.0.dev7-py3-none-any.whl \
    zeroc_ice-3.6.5-cp36-cp36m-linux_x86_64.whl
```

## Testing

Testing is done through [pytest][d4] and can be triggered by running this command:

```bash
poetry run pytest
```

By default only *local* tests will be performed, all tests that require the connection
to an actual OMERO instance are disabled. To activate them you need to pass the
`--online` flag to the pytest call and a corresponding file `site_specific.py` needs to
be present in `tests/online/settings/` that contains the settings on how to connect to
your OMERO, plus the mapping of object and user IDs. See `tests/resources/settings/` for
a template file, copy it to the repository root and make your adjustments there. Then
run this command:

```bash
poetry run pytest --online
```

NOTE: each online test does a connectivity check first, if the OMERO server specified in
the site-specific settings can't be reached they will be skipped (instead of generating
tons of failed test results).

### Prepare an OMERO instance for tests

It is recommended to test against an isolated OMERO instance to avoid messing up any
production data. The script in `resources/omero-recipes/setup-ubuntu-20-04.sh` can be
used to install OMERO quickly on Ubuntu 20.04. A reasonable approach would be this:

- Create a VM / container with a basic Ubuntu 20.04 installation.
- Copy the OMERO-setup-script into the VM / container.
- Run the setup script *from within* the VM / container.

Once OMERO is running, you can use the preparation script to create the required groups,
users, projects, ... in that OMERO instance. Please note that the preparation script is
meant to be run **from the HRM-OMERO development environment** (i.e. not from within
your shiny new OMERO-VM)!

Please **note** that values for the OMERO server address, passwords for the omero `root`
user and the additional users created during the preparation can be *pre-seeded* by
providing an input file, see `resources/scripts/omero-seeds.inc.sh` for an example.

Assuming you copied the seeds file to `my-omero-seeds.inc.sh`, you can simply run the
preparation script like this:

```bash
bash resources/scripts/prepare-omero-for-testing.sh \
    resources/scripts/my-omero-seeds.inc.sh \
    tests/resources/settings/site_specific.yml
```

## Generating Documentation

The project is using [pdoc][d2] for generating API documentation. To update or (re-)
generate the HTML documentation use this `poetry` command:

```bash
poetry run pdoc --docformat numpy --output-directory docs/ src/hrm_omero/
```

## ToDo list

- [x] sort tree levels (users, projects, ...) alphabetically, by default they are
      returned in the same order as OMERO is iterating them
- [x] use "key-value pairs" for the HRM job parameter summaries
- [x] trees for different groups
  - [x] (REJECTED) ~~requesting groups through a commandline option~~
- [x] logging
  - [x] proper logging ([loguru][d3])
  - [x] separate logfile for the connector
  - [x] adjust log verbosity through a parameter
  - [x] adjust log verbosity through the configuration file
- [x] allow debug logging of the "omero import" call
  - [x] (REJECTED) ~~requested through a command line argument~~
  - [x] through the configuration file
- [x] (REJECTED) ~~offer download of OME-TIFFs~~
- [x] don't use a command line parameter for the OMERO password
- [x] lift assumption that datasets are always members of a project in OMERO
- [x] create target directory for thumbnails in case it doesn't exist
- [x] create documentation on the `OMERO_USERDIR` configuration
- [x] make log verbosity setting optional in the configuration file, otherwise
      `Adding a file sink for logging failed: Level '' does not exist` is issued
      from `hrm_omero.cli:logger_add_file_sink` if nothing is present
- [ ] try to catch "assert failed" errors when uploading data to OMERO, this usually
      indicates that the file / fileset was refused by Bio-Formats
- [x] retain structure of complex multi-file datasets like Olympus `.vsi` that
      expects files to be in specific sub-directories etc.
- [ ] add group-write permissions to files and directories created by the connector

## Planned features

- [ ] add command line action to create new projects and datasets in OMERO
- [ ] speed up tree-loading by avoiding the necessary repeated calls to the connector

[d1]: https://python-poetry.org/
[d2]: https://pdoc.dev/
[d3]: https://github.com/Delgan/loguru
[d4]: https://pytest.org/
