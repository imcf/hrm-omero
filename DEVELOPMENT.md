# Developing the HRM-OMERO connector

## Generating Documentation

```bash
poetry run pdoc --docformat numpy --output-directory docs/ src/hrm_omero/
```

## ToDo list

- trees for different groups
  - requesting groups through a commandline option
- proper logging, separate logfile for the connector
- redirect logging of CLI
- offer download of OME-TIFFs?
