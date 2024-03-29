# Changelog

## Planned for 1.0.0

### New in 1.0.0

### Changes in 1.0.0

* The previously deprecated option of providing the password through a command line
  argument has been removed.

### Fixes in 1.0.0

## 0.4.0

### New in 0.4.0

* An environment variable `OMERO_PASSWORD` can (and should!) now be used to supply the
  sensitive part of the user credentials that are necessary to connect to OMERO. This
  avoids having the password as plain-text in the system's process list (e.g. when
  calling `ps fu -e` or similar) and also prevents it from showing up in an annotated
  stack trace in case an uncaught exception is raised.
* Log level of the HRM-OMERO connector itself can now be set through the configuration
  option `OMERO_CONNECTOR_LOGLEVEL` in the HRM config file.
* Log messages of the connector will also be placed in a separate log file in the
  default location defined via `HRM_LOG` in the HRM config file. This can be disabled by
  setting `OMERO_CONNECTOR_LOGFILE_DISABLED=true`.
* Debug logging for the OMERO *import call* can now be requested be setting the
  configuration option `OMERO_DEBUG_LOG` in the HRM config file.
* `hrm_omero.hrm.parse_summary()` has been added to provide a function for parsing the
  parameter summary from an HRM job into a (nested) dict.
* `hrm_omero.hrm.parse_job_basename()` has been added to identify the base name of all
  files that belong to the set of results from a certain HRM job.
* `hrm_omero.omero.add_annotation_keyvalue()` can be used to add so-called [Map
  Annotations][c4] (key-value pairs) to objects in OMERO.
* `hrm_omero.omero.find_recently_imported()` tries to identify an image in OMERO using
  the import timestamp and the object label as criteria.
* A decorator `hrm_omero.decorators.connect_and_set_group()` is now available that can
  be used with functions that require a valid connection plus an OMERO object identifier
  pair (submitted on the command line as "`G:4:Image:12345`" or similar, passed on to
  the decorated function as `obj_type` and `obj_id`).
* `hrm_omero.misc.printlog()` can be used to push a message to the log and stdout.
* A class `hrm_omero.misc.OmeroId` provides parsing, validation and access to all
  group-qualified OMERO object IDs (commonly passed as function parameter `id_str`
  throughout the existing code).
* The CLI has a new optional parameter `--dry-run` that prevents any action from being
  performed, instead the name of the function and the corresponding parameters that
  would be called are printed to stdout.
* Unit tests using [pytest][c2] and [pytest-cov][c3].

### Changes in 0.4.0

* Uploading images to OMERO into another group than the user's default one is now
  properly supported.
* HRM job parameter summaries are now being added as OMERO ["Map Annotations"][c4]
  instead of simply being a comment string.
* Formats like e.g. Olympus `.vsi` requiring their files to be placed in a specific
  directory structure are now properly supported.
* Tree levels (users, projects, ...) are now sorted alphabetically instead of the
  (seemingly) random order as they are returned by OMERO with the exception of the
  current user always being listed first on the group level, followed by their
  colleagues.
* *Datasets* in OMERO that are not associated to a *Project* will no longer be ignored
  but rather be shown on the same level than the user's projects, just as OMERO.web and
  OMERO.insight are doing it.
* The target directory for downloading preview thumbnails from OMERO will be created
  automatically in case it doesn't exist yet.
* The command line parameter `--password` (or `-w`) is now *deprecated* in favor of
  using the environment variable described above.
* The following functions are now *deprecated* and will be removed in a future release.
  * `hrm_omero.omero.connect()`
  * `hrm_omero.cli.parse_arguments()`
* Functions `hrm_omero.transfer.to_omero()` and `hrm_omero.transfer.from_omero()` are
  now raising a `ValueError` in case the provided `id_str` is malformed.
* Various improvements on log messages.
* Unit string literal `µm` is no longer converted to `um` in parameter summaries.
* New dependencies: [Pillow][c1]

### Fixes in 0.4.0

* Thumbnail download has been adapted to recent code changes in OMERO.

[c1]: https://pypi.org/project/Pillow/
[c2]: https://docs.pytest.org/
[c3]: https://pypi.org/project/pytest-cov/
[c4]: https://docs.openmicroscopy.org/omero/5.6/developers/Python.html#write-data
