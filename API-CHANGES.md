# API Changes

This document contains the API changes compared to the ["integrated" HRM-OMERO
connector][1] that used to be shipped with the HRM itself previously.

## [`hrm_config`][2]

| `hrm_config`       | `hrm_omero`          |
|--------------------|----------------------|
| `parse_hrm_conf()` | `hrm.parse_config()` |
| `check_hrm_conf()` | `hrm.check_config()` |

## [`ome_hrm`][1]

| `ome_hrm`                 | `hrm_omero`                        |
|---------------------------|------------------------------------|
| `omero_login()`           | `omero.connect()`                  |
| `check_credentials()`     | `omero.check_credentials()`        |
| `gen_obj_dict()`          | `tree.gen_obj_dict()`              |
| `gen_children()`          | `tree.gen_children()`              |
| `gen_base_tree()`         | `tree.gen_base_tree()`             |
| `gen_group_tree()`        | `tree.gen_group_tree()`            |
| `tree_to_json()`          | `formatting.tree_to_json()`        |
| `print_children_json()`   | `formatting.print_children_json()` |
| `gen_parameter_summary()` | `hrm.job_parameter_summary()`      |
| `omero_to_hrm()`          | `transfer.from_omero()`            |
| `hrm_to_omero()`          | `transfer.to_omero()`              |
| `download_thumb()`        | `transfer.fetch_thumbnail()`       |


[1]: https://github.com/aarpon/hrm/blob/master/bin/ome_hrm.py
[2]: https://github.com/aarpon/hrm/blob/master/bin/hrm_config.py
