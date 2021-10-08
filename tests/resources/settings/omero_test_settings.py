"""Settings for running tests against an actual OMERO instance."""


def _fmt(raw_string):
    """Helper function to replace the UID / GID / ... placeholders."""
    result = raw_string
    for pair in IDS_TO_REPLACE:
        result = result.replace("{{" + pair[0] + "}}", pair[1])
    return result


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

_BASE_TREE_DEFAULT = _fmt(
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


_BASE_TREE_OTHER = _fmt(
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

_ROOT_TREE = (
    """
    [
"""
    + _BASE_TREE_DEFAULT
    + """,
"""
    + _BASE_TREE_OTHER
    + """
    ]
"""
)

SETTINGS = {
    "hostname": "omero.example.xy",  # the OMERO server IP address or hostname
    "port": None,  # the port to connect to the OMERO server
    "username": "hrm-test-01",  # a valid username on the OMERO server
    # "password": "w41dFee",  # the corresponding password for the OMERO user
    # "username": "hrm-test-02",  # a valid username on the OMERO server
    # "password": "H011aaaa",  # the corresponding password for the OMERO user
    "default_group": _fmt("{{GID_1}}"),
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
    "retrieveChildren": [
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
    ],
    "gen_group_tree__none": _BASE_TREE_DEFAULT,
    "gen_group_tree": [
        {"group": None, "tree": _BASE_TREE_DEFAULT},
        {"group": _fmt("{{GID_1}}"), "tree": _BASE_TREE_DEFAULT},
        {"group": _fmt("{{GID_2}}"), "tree": _BASE_TREE_OTHER},
    ],
}
