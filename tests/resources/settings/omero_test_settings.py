"""Settings for running tests against an actual OMERO instance."""


def _replace_ids(raw_string):
    result = (
        raw_string.replace("{{GID}}", GID)
        .replace("{{EID}}", EID)
        .replace("{{EID_OTHER}}", EID_OTHER)
        .replace("{{GID_OTHER}}", GID_OTHER)
    )
    return result


EID = "5809"
GID = "9"
EID_OTHER = "5810"
GID_OTHER = "903"

_BASE_TREE_DEFAULT = _replace_ids(
    """
    {
        "label": "SYS Test HRM-OMERO 1",
        "class": "ExperimenterGroup",
        "owner": null,
        "id": "ExperimenterGroup:{{GID}}",
        "children": [
            {
                "label": "Test-01 HRM-OMERO",
                "class": "Experimenter",
                "owner": {{EID}},
                "id": "G:{{GID}}:Experimenter:{{EID}}",
                "children": [],
                "load_on_demand": true
            },
            {
                "label": "Test-02 HRM-OMERO",
                "class": "Experimenter",
                "owner": {{EID_OTHER}},
                "id": "G:{{GID}}:Experimenter:{{EID_OTHER}}",
                "children": [],
                "load_on_demand": true
            }
        ]
    }
"""
)


_BASE_TREE_OTHER = _replace_ids(
    """
    {
        "label": "SYS Test HRM-OMERO 2",
        "class": "ExperimenterGroup",
        "owner": null,
        "id": "ExperimenterGroup:{{GID_OTHER}}",
        "children": [
            {
                "label": "Test-01 HRM-OMERO",
                "class": "Experimenter",
                "owner": {{EID}},
                "id": "G:{{GID_OTHER}}:Experimenter:{{EID}}",
                "children": [],
                "load_on_demand": true
            },
            {
                "label": "Test-02 HRM-OMERO",
                "class": "Experimenter",
                "owner": {{EID_OTHER}},
                "id": "G:{{GID_OTHER}}:Experimenter:{{EID_OTHER}}",
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
    "default_group": "9",
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
            "omero_id": "G:9:Experimenter:5809",
            "json_result": """
                [
                    {
                        "children": [],
                        "class": "Project",
                        "id": "G:9:Project:12205",
                        "label": "Proj01",
                        "load_on_demand": true,
                        "owner": "hrm-test-01"
                    },
                    {
                        "children": [],
                        "class": "Dataset",
                        "id": "G:9:Dataset:47057",
                        "label": "NoProj--Dset01",
                        "load_on_demand": true,
                        "owner": "hrm-test-01"
                    }
                ]
            """,
        },
        {
            "omero_id": "G:9:Project:12205",
            "json_result": """
                [
                    {
                        "children": [],
                        "class": "Dataset",
                        "id": "G:9:Dataset:47056",
                        "label": "Proj01--Dset01",
                        "load_on_demand": true,
                        "owner": "hrm-test-01"
                    }
                ]
            """,
        },
    ],
    "gen_group_tree__none": _BASE_TREE_DEFAULT,
    "gen_group_tree": [
        {"group": None, "tree": _BASE_TREE_DEFAULT},
        {"group": GID, "tree": _BASE_TREE_DEFAULT},
        {"group": GID_OTHER, "tree": _BASE_TREE_OTHER},
    ],
}
