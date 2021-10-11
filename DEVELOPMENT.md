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

See the example script in `resources/scripts/prepare-omero-for-testing.sh` on how to set
up an OMERO instance so it can be used with the `--online` tests. Note that currently
the settings file will still need to be adjusted for *user* and *object IDs*!

## Generating Documentation

The project is using [pdoc][d2] for generating API documentation. To update or (re-)
generate the HTML documentation use this `poetry` command:

```bash
poetry run pdoc --docformat numpy --output-directory docs/ src/hrm_omero/
```

## ToDo list

- [x] use "key-value pairs" for the HRM job parameter summaries
- [x] trees for different groups
  - [x] (REJECTED) requesting groups through a commandline option
- [ ] logging
  - [x] proper logging ([loguru][d3])
  - [ ] separate logfile for the connector
  - [x] adjust log verbosity through a parameter
  - [x] adjust log verbosity through the configuration file
- [x] allow debug logging of the "omero import" call
  - [x] (REJECTED) requested through a command line argument
  - [x] through the configuration file
- [x] (REJECTED) offer download of OME-TIFFs
- [x] don't use a command line parameter for the OMERO password
- [ ] add command line action to create new projects and datasets in OMERO
- [x] lift assumption that datasets are always members of a project in OMERO
- [x] create target directory for thumbnails in case it doesn't exist

[d1]: https://python-poetry.org/
[d2]: https://pdoc.dev/
[d3]: https://github.com/Delgan/loguru
[d4]: https://pytest.org/
