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

## Generating Documentation

```bash
poetry run pdoc --docformat numpy --output-directory docs/ src/hrm_omero/
```

## ToDo list

- trees for different groups
  - requesting groups through a commandline option
- logging
  - proper logging (loguru) [DONE]
  - separate logfile for the connector
  - adjust log verbosity through a parameter [DONE]
  - adjust log verbosity through the configuration file
- offer download of OME-TIFFs?
[d1]: https://python-poetry.org/
