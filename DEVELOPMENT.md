# Developing the HRM-OMERO connector

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
