"""Site-specific settings for the online tests."""


HOSTNAME = "local-omero"  # the OMERO server address
PORT = None  # the port to connect to the OMERO server (default= 4064)
USERNAME = "hrm-test-01"  # a valid username on the OMERO server
# PASSWORD = None  # 'None' means the OMERO_PASSWORD environment variable will be used
PASSWORD = "H011aaaaW41dFee"  # the corresponding password for the OMERO user
# USERNAME = "hrm-test-02",  # a valid username on the OMERO server
# PASSWORD = "Alt3rKl4baut3r",  # the corresponding password for the OMERO user


IDS_TO_REPLACE = [
    ("UID_1", "2"),
    ("UID_2", "3"),
    ("GID_1", "3"),
    ("GID_2", "4"),
    ("U1__PID_1", "Project:1"),
    ("U1__PID_1__DSID_1", "Dataset:1"),
    ("U1__PID_1__DSID_2", "Dataset:2"),
    ("U1__DSID_1", "Dataset:3"),
    ("U1__IID_1", "Image:1"),
]
