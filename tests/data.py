"""Mock and dummy data for unit tests."""

import os.path


### stdout help messages ###

# a regular expression matching stdout/stderr if --help is called or an invalid
# combination of parameters is given:
RE_HELP = r"usage: [a-z_-]+ \[-h\] \[-v\] \[--version\] \[-c CONFIG\] \[--dry-run\]"


### HRM configuration file data mocks ###

CONF_SHORT = """
# OMERO_HOSTNAME="omero"
OMERO_HOSTNAME="omero.mynetwork.xy"
# OMERO_HOSTNAME="localhost"
OMERO_PORT="4064"
"""

CONF_LONG = (
    CONF_SHORT
    + """
# OMERO_PKG specifies the path where the "OMERO.server" package is installed
OMERO_PKG="/opt/OMERO/OMERO.server"
"""
)

CONF_SEMICOLON = 'FOO="one" ; BAR="two"'

CONF_NOEQUALS = "KEY_WITHOUT_VALUE"

CONF_COMMENT = 'TRIPLE="reloaded"  # whatever that means'


### image files and HRM job parameter summaries ###

BASE_DIR = os.path.join("tests", "resources", "parameter-summaries")
FNAME_VALID = os.path.join(BASE_DIR, "valid-summary.txt")
FNAME_VALID_IMAGE = os.path.join(BASE_DIR, "dummy_0123456789abc_hrm.png")
FNAME_INVALID_HEADERS = os.path.join(BASE_DIR, "invalid-summary-duplicate-headers.txt")
FNAME_INVALID_PARAMS = os.path.join(BASE_DIR, "invalid-summary-duplicate-params.txt")


### mock strings as returned by OMERO ###

IMPORT_YAML_VALID = "- Fileset: 54321\n  Image:\n  - 778899\n"
IMPORT_YAML_INVALID = "- Fileset: 54321\n  XImage:\n  - 778899\n"
IMPORT_YAML_INVALID_MULTI = "- Fileset: 54321\n  Image:\n  - 778899\n  - 118899\n"
