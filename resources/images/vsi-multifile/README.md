# Olympus VSI "multifile" test dataset

A publicly available dataset in the proprietary [Olympus VSI][1] format intended
for testing file readers and other related mechanisms.

Key properties / requirements:

* overall size is as small as possible (~200 kiB in this case)
* dataset consists of a top-level `.vsi` file plus a subfolder structure
  containing one or more `.ets` files

**IMPORTANT**: this dataset was heavily postprocessed (see the section below),
it is purely meant to have a valid example of the file format structure.

## Dataset Information

### Image Dimensions

* channels: 2 (405, 488)
* size X: 1645
* size Y: 1682
* size Z: 11

### Software Version

The software used to acquire and postprocess the dataset.

* cellSens Dimension v3.1 (Build 21199)

### Postprocessing

The following steps were applied to reduce the size of the dataset:

* cropping
* background subtraction
* rank filter
* NxN filter
* JPEG 2000 compression

[1]: https://www.olympus-lifescience.com/
