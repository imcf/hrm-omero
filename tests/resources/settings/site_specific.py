"""Site-specific settings for the online tests."""

from pathlib import Path

import yaml


HOSTNAME = "local-omero"  # the OMERO server address
PORT = None  # the port to connect to the OMERO server (default= 4064)
USERNAME = "hrm-test-01"  # a valid username on the OMERO server
# PASSWORD = None  # 'None' means the OMERO_PASSWORD environment variable will be used
PASSWORD = "H011aaaaW41dFee"  # the corresponding password for the OMERO user
# USERNAME = "hrm-test-02",  # a valid username on the OMERO server
# PASSWORD = "Alt3rKl4baut3r",  # the corresponding password for the OMERO user


# load the YAML file called 'site_specific' located in the same directory:
yaml_file = Path(__file__).parent.absolute() / "site_specific.yml"
with open(yaml_file, "r", encoding="utf-8") as stream:
    SITE_SPECIFIC = yaml.safe_load(stream)
