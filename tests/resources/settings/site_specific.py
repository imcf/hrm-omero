"""Site-specific settings for the online tests."""


HOSTNAME = "omero.example.xy"  # the OMERO server IP address or hostname
PORT = None  # the port to connect to the OMERO server (default= 4064)
USERNAME = "hrm-test-01"  # a valid username on the OMERO server
PASSWORD = None  # 'None' means the OMERO_PASSWORD environment variable will be used
# PASSWORD = "w41dFee"  # the corresponding password for the OMERO user
# USERNAME = "hrm-test-02",  # a valid username on the OMERO server
# PASSWORD = "H011aaaa",  # the corresponding password for the OMERO user


IDS_TO_REPLACE = [
    ("UID_1", "5809"),
    ("UID_2", "5810"),
    ("GID_1", "9"),
    ("GID_2", "903"),
    ("U1__PID_1", "Project:12221"),
    ("U1__PID_1__DSID_1", "Dataset:47119"),
    ("U1__PID_1__DSID_2", "Dataset:47120"),
    ("U1__DSID_1", "Dataset:47121"),
]
