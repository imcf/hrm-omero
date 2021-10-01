"""Settings for running tests against an actual OMERO instance."""

SETTINGS = {
    "hostname": "omero.example.xy",  # the OMERO server IP address or hostname
    "username": "testuser",  # a valid username on the OMERO server
    # the password can be specified here - if the entry is not present / commented out
    # the tests require the environment variable $OMERO_PASSWORD to be set and exported
    "password": "testpass",
    "OMEROtoHRM": [
        # a list of dicts containing IDs of images in OMERO and their file name
        {
            "id_str": "G:4:Image:1567250",
            "expected_name": "test-image.tif",
        },
        {
            "id_str": "G:753:Image:1569216",
            "expected_name": "2014-02-28-dapi-phalloidin-atub_0123456789abc_hrm.png",
        },
    ],
}
