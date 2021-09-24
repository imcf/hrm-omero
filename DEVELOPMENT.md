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
    hrm-omero==0.3.2.dev0
```

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

[d1]: https://python-poetry.org/
[d2]: https://pdoc.dev/
[d3]: https://github.com/Delgan/loguru
