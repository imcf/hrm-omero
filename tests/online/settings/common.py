"""Settings for running tests against an actual OMERO instance."""

import pytest


def _fmt(raw_string):
    """Helper function to replace the UID / GID / ... placeholders."""
    result = raw_string
    for pair in IDS_TO_REPLACE:
        result = result.replace("{{" + pair[0] + "}}", pair[1])
    return result


try:
    from settings.site_specific import (
        HOSTNAME,
        PORT,
        USERNAME,
        IDS_TO_REPLACE,
        PASSWORD,
    )
except ImportError:
    pytest.skip(
        "Can't import 'settings/site_specific.py' file required for online tests!",
        allow_module_level=True,
    )

if PORT is None:
    PORT = 4064


BASE_TREE_DEFAULT = _fmt(
    """
        {
            "label": "SYS Test HRM-OMERO 1",
            "class": "ExperimenterGroup",
            "owner": null,
            "id": "ExperimenterGroup:{{GID_1}}",
            "children": [
                {
                    "label": "Test-01 HRM-OMERO",
                    "class": "Experimenter",
                    "owner": {{UID_1}},
                    "id": "G:{{GID_1}}:Experimenter:{{UID_1}}",
                    "children": [],
                    "load_on_demand": true
                },
                {
                    "label": "Test-02 HRM-OMERO",
                    "class": "Experimenter",
                    "owner": {{UID_2}},
                    "id": "G:{{GID_1}}:Experimenter:{{UID_2}}",
                    "children": [],
                    "load_on_demand": true
                }
            ]
        }
    """
)


BASE_TREE_OTHER = _fmt(
    """
        {
            "label": "SYS Test HRM-OMERO 2",
            "class": "ExperimenterGroup",
            "owner": null,
            "id": "ExperimenterGroup:{{GID_2}}",
            "children": [
                {
                    "label": "Test-01 HRM-OMERO",
                    "class": "Experimenter",
                    "owner": {{UID_1}},
                    "id": "G:{{GID_2}}:Experimenter:{{UID_1}}",
                    "children": [],
                    "load_on_demand": true
                },
                {
                    "label": "Test-02 HRM-OMERO",
                    "class": "Experimenter",
                    "owner": {{UID_2}},
                    "id": "G:{{GID_2}}:Experimenter:{{UID_2}}",
                    "children": [],
                    "load_on_demand": true
                }
            ]
        }
    """
)

ROOT_TREE = (
    """
    [
    """
    + BASE_TREE_DEFAULT
    + """,
    """
    + BASE_TREE_OTHER
    + """
    ]
    """
)

GID_1 = _fmt("{{GID_1}}")
GID_2 = _fmt("{{GID_2}}")


retrieveChildren = [
    {
        "omero_id": _fmt("G:{{GID_1}}:Experimenter:{{UID_1}}"),
        "json_result": _fmt(
            """
                [
                    {
                        "children": [],
                        "class": "Project",
                        "id": "G:{{GID_1}}:{{U1__PID_1}}",
                        "label": "Proj01",
                        "load_on_demand": true,
                        "owner": "hrm-test-01"
                    },
                    {
                        "children": [],
                        "class": "Dataset",
                        "id": "G:{{GID_1}}:{{U1__DSID_1}}",
                        "label": "NoProj--Dset01",
                        "load_on_demand": true,
                        "owner": "hrm-test-01"
                    }
                ]
            """
        ),
    },
    {
        "omero_id": _fmt("G:{{GID_1}}:{{U1__PID_1}}"),
        "json_result": _fmt(
            """
                [
                    {
                        "children": [],
                        "class": "Dataset",
                        "id": "G:{{GID_1}}:{{U1__PID_1__DSID_1}}",
                        "label": "Proj01--Dset01",
                        "load_on_demand": true,
                        "owner": "hrm-test-01"
                    },
                    {
                        "children": [],
                        "class": "Dataset",
                        "id": "G:{{GID_1}}:{{U1__PID_1__DSID_2}}",
                        "label": "upload-target",
                        "load_on_demand": true,
                        "owner": "hrm-test-01"
                    }
                ]
            """
        ),
    },
]

gen_group_tree = [
    {"group": None, "tree": BASE_TREE_DEFAULT},
    {"group": _fmt("{{GID_1}}"), "tree": BASE_TREE_DEFAULT},
    {"group": _fmt("{{GID_2}}"), "tree": BASE_TREE_OTHER},
]


download_image = [
    {
        "image_id": _fmt("{{U1__IID_1}}"),
        "gid": GID_1,
        "filename": "3ch-dapi-pha-atub.ics",
        "sha1sum": "48ee0def0bbaf94e629114df6a306604d38dccdd",
    }
]

download_image_other_group = [
    {
        "image_id": _fmt("{{U2__G2_IID_1}}"),
        "gid": GID_2,
        "filename": "3ch-dapi-pha-atub.ics",
        "sha1sum": "48ee0def0bbaf94e629114df6a306604d38dccdd",
    }
]

_RESULTS = "tests/resources/hrm-results"
import_image = [
    {
        "filename": f"{_RESULTS}/01/3ch-dapi-pha-atub_0123456789abc_hrm.ics",
        "sha1sum": "48ee0def0bbaf94e629114df6a306604d38dccdd",
        "target_id": _fmt("G:{{GID_1}}:{{U1__PID_1__DSID_2}}"),
        "fset_count": 1,
        "fset_size": 30438,
    }
]

import_messages = [
    "Using import target: Dataset",
    "FILESET_UPLOAD_PREPARATION",
    "FILESET_UPLOAD_START",
    "FILE_UPLOAD_STARTED",
    "FILE_UPLOAD_COMPLETE",
    "IMPORT_STARTED",
    "PIXELDATA_PROCESSED",
    "IMPORT_DONE",
]
