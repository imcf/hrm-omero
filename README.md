# The HRM-OMERO connector

This project provides a connector to allow for communication between an [HRM (Huygens
Remote Manager)][hrm] and an [OMERO server][omero].

Its purpose is to simplify the data transfer by allowing raw images to be downloaded
from OMERO as well as uploading deconvolution results back to OMERO directly from within
the HRM web interface.

## Setup

### Installing requirements

#### CentOS / RHEL 7 and 8

```bash
# install the build-time requirements for Python 3.6 and Java 1.8 for Bio-Formats
sudo yum install \
    python36 \
    python36-devel \
    openssl-devel \
    bzip2-devel \
    readline-devel \
    gcc-c++ \
    java-1.8.0-openjdk

# define the target path for the virtual environment:
HRM_OMERO_VENV="/opt/venvs/hrm-omero"

# create a Python 3.6 virtual environment:
python3 -m venv $HRM_OMERO_VENV
```

#### Ubuntu 20.04

```bash
# FIXME: check build-time requirements and update here!

# define the target path for the virtual environment:
HRM_OMERO_VENV="/opt/venvs/hrm-omero"

# create a Python 3.6 virtual environment:
python -m venv $HRM_OMERO_VENV
```

### Installing the HRM-OMERO package

```bash
# upgrade pip, install wheel:
$HRM_OMERO_VENV/bin/pip install --upgrade pip wheel

# install the connector - please note that it takes quite a while (~15min) as it needs
# to build (compile) the ZeroC Ice bindings:
$HRM_OMERO_VENV/bin/pip install hrm-omero

# from now on you can simply call the connector using its full path, there is no need
# to pre-activate the virtual environment - you could even drop your pyenv completely:
$HRM_OMERO_VENV/bin/ome-hrm --help

# this is even usable as a drop-in replacement for the legacy `ome_hrm.py` script:
cd $PATH_TO_YOUR_HRM_INSTALLATION/bin
mv "ome_hrm.py" "__old__ome_hrm.py"
ln -s "$HRM_OMERO_VENV/bin/ome-hrm" "ome_hrm.py"
```

## Debugging

By default the connector will be rather silent as otherwise the log files will be
cluttered up quite a bit on a production system. However, it is possible to increase the
log level by specifying `-v`, `-vv` and so on.

Since this is not useful when being operated through the HRM web interface (which is
the default) it's also possible to set the verbosity level by adjusting the
`OMERO_CONNECTOR_LOGLEVEL` in `/etc/hrm.conf`.

Valid settings are `"SUCCESS"`, `"INFO"`, `"DEBUG"` and `"TRACE"`. If the option is
commented out in the configuration file, the level will be set to `WARNING`. Log
messages produced by the connector when called by HRM will usually end up in the web
server's error log (as they go to `stderr`).

## Example Usage

Store username and password in variables, export the OMERO_PASSWORD variable:

```bash
read OMERO_USER
read -s OMERO_PASSWORD
export OMERO_PASSWORD   # use 'set --export OMERO_PASSWORD $OMERO_PASSWORD' for fish
```

### Verifying Credentials

```bash
ome-hrm \
    --user $OMERO_USER \
    checkCredentials
```

### Fetching OMERO tree information

Set the `--id` parameter according to what part of the tree should be retrieved:

```bash
OMERO_ID="ROOT"                # fetches the base tree view for the current user
OMERO_ID="G:4:Experimenter:9"  # fetches the projects of user '9' in group '4'
OMERO_ID="G:4:Project:12345"   # fetches the datasets of project '12345'
OMERO_ID="G:4:Dataset:65432"   # lists the images of dataset '65432'
```

Then run the actual command to fetch the information, the result will be a JSON tree:

```bash
ome-hrm \
    --user $OMERO_USER \
    retrieveChildren \
    --id "$OMERO_ID"
```

For example this could be the output when requesting `"G:4:Dataset:65432"`:

```json
[
    {
        "children": [],
        "class": "Image",
        "id": "G:4:Image:1311448",
        "label": "4321_mko_ctx_77.tif",
        "owner": "somebody"
    },
    {
        "children": [],
        "class": "Image",
        "id": "G:4:Image:1566150",
        "label": "test-image.tif",
        "owner": "somebody"
    }
]
```

### Downloading an image from OMERO

This will fetch the second image from the example tree above and store it in `/tmp/`:

```bash
ome-hrm \
    --user $OMERO_USER \
    OMEROtoHRM \
    --imageid "G:4:Image:1566150" \
    --dest /tmp/
```

### Uploading an image from the local file system to OMERO

The command below will import a local image file into the example dataset from above:

```bash
ome-hrm \
    --user $OMERO_USER \
    HRMtoOMERO \
    --dset "G:4:Dataset:65432" \
    --file test-image.tif
```

[hrm]: https://huygens-rm.org/
[omero]: https://www.openmicroscopy.org/omero/
