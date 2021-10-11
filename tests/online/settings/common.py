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

GID = _fmt("{{GID_1}}")


retrieveChildren = [
    {
        "omero_id": _fmt("G:{{GID_1}}:Experimenter:5809"),
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


SETTINGS = {
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
    "gen_group_tree__none": BASE_TREE_DEFAULT,
}
