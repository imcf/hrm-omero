# The HRM-OMERO connector

This project provides a connector to allow for communication between an [HRM (Huygens
Remote Manager)][1] and an [OMERO server][2].

Its purpose is to simplify the data transfer by allowing raw images to be downloaded
from OMERO as well as uploading deconvolution results back to OMERO directly from within
the HRM web interface.

## Example Usage

Store you username and password in variables:

```bash
read OMEROUSER
read OMEROPW
```

### Verify Credentials

```bash
ome-hrm \
    --user $OMEROUSER \
    --password $OMEROPW \
    checkCredentials
```

### Fetch OMERO tree information

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
    --user $OMEROUSER \
    --password $OMEROPW \
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

### Download an image from OMERO

This will fetch the second image from the example tree above and store it in `/tmp/`:

```bash
ome-hrm \
    --user $OMEROUSER \
    --password $OMEROPW \
    OMEROtoHRM \
    --imageid "G:4:Image:1566150" \
    --dest /tmp/
```

### Upload an image from the local file system to OMERO

The command below will import a local image file into the example dataset from above:

```bash
ome-hrm \
    --user $OMEROUSER \
    --password $OMEROPW \
    HRMtoOMERO \
    --dset "G:4:Dataset:65432" \
    --file test-image.tif
```

[1]: https://huygens-rm.org/
[2]: https://www.openmicroscopy.org/
