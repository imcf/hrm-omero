# Changelog

## 0.3.2

### New

* Unit tests using [pytest][c2] and [pytest-cov][c3] (incomplete).

### Changes

* Uploading images to OMERO into another group than the user's default one is now
  properly supported.
* The function `hrm_omero.omero.connect()` is now deprecated and will be removed in a
  subsequent release.
* Functions `hrm_omero.transfer.to_omero()` and `hrm_omero.transfer.from_omero()` are
  now raising a `ValueError` in case the provided `id_str` is malformed.
* Various improvements on log messages.
* Unit string literal `µm` is no longer converted to `um` in parameter summaries.
* New dependencies: [Pillow][c1]

### Fixes

* Thumbnail download has been adapted to recent code changes in OMERO.

[c1]: https://pypi.org/project/Pillow/
[c2]: https://docs.pytest.org/
[c3]: https://pypi.org/project/pytest-cov/
