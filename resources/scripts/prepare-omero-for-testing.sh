#!/bin/bash

# log in with an account that can create users and groups:
omero login

# create two test groups
omero group add --type read-annotate "SYS Test HRM-OMERO 1"
omero group add --type read-annotate "SYS Test HRM-OMERO 2"

# NOTE: the above commands will produce output similar to this below:
# ---
# Added group SYS Test HRM-OMERO 1 (id=9) with permissions rwra--
# ---
# make sure to set the group ID variables accordingly:
GID_1=9
GID_2=903

# generate random 16-char passwords using letters (upper- and lower-case) and digits
U1_PW=$(
    tr -dc A-Za-z0-9 </dev/urandom | head -c 16
    echo ''
)
U2_PW=$(
    tr -dc A-Za-z0-9 </dev/urandom | head -c 16
    echo ''
)

# create two users, add them to the first group:
omero user add "hrm-test-01" Test-01 HRM-OMERO --userpassword "$U1_PW" --group-id "$GID_1"
omero user add "hrm-test-02" Test-02 HRM-OMERO --userpassword "$U2_PW" --group-id "$GID_1"

# again, make sure to parse the newly created user IDs from the output similar to this:
# ---
# Added user hrm-test-01 (id=5810) with password
# ---
UID_1=5810
UID_2=5811

echo "Adding the users to the second group..."
omero group adduser --id "$GID_2" --user-id "$UID_1" --quiet
omero group adduser --id "$GID_2" --user-id "$UID_2" --quiet

echo "Reconnecting using the newly created user..."
omero logout
omero login -u "hrm-test-01" -w "$U1_PW"

echo "Creating a project-dataset-tree..."
project=$(omero obj new Project name='Proj01' --quiet)
dataset=$(omero obj new Dataset name='Proj01--Dset01' --quiet)
omero obj new ProjectDatasetLink parent="$project" child="$dataset" --quiet
echo "#ts# (\"U1__PID_1\", \"$project\"),"
echo "#ts# (\"U1__PID_1__DSID_1\", \"$dataset\"),"

echo "Importing a test image there..."
image=$(omero import -d "$dataset" resources/images/3ch-dapi-pha-atub.ics --quiet)
echo "#ts# (\"U1__IID_1\", \"$image\"),"

echo "Creating another dataset in that project to be used as an upload target..."
dataset=$(omero obj new Dataset name='upload-target' --quiet)
omero obj new ProjectDatasetLink parent="$project" child="$dataset" --quiet
echo "#ts# (\"U1__PID_1__DSID_2\", \"$dataset\"),"

echo "Creating a dataset without a project (top-level)..."
dataset=$(omero obj new Dataset name='NoProj--Dset01' --quiet)
echo "#ts# (\"U1__DSID_1\", \"$dataset\"),"

echo "Reconnecting using the second user..."
omero logout
omero login -u "hrm-test-02" -w "$U2_PW"

echo "Creating a project-dataset-tree..."
project=$(omero obj new Project name='U2-Proj01' --quiet)
dataset=$(omero obj new Dataset name='U2-Proj01--Dset01' --quiet)
omero obj new ProjectDatasetLink parent="$project" child="$dataset" --quiet
echo "#ts# (\"U2__PID_1\", \"$project\"),"
echo "#ts# (\"U2__PID_1__DSID_1\", \"$dataset\"),"

dataset=$(omero obj new Dataset name='U2-Proj01--Dset02' --quiet)
omero obj new ProjectDatasetLink parent="$project" child="$dataset" --quiet
echo "#ts# (\"U2__PID_1__DSID_2\", \"$dataset\"),"

echo "Creating some datasets without a project (top-level)..."
dataset=$(omero obj new Dataset name='U2-NoProj--Dset01' --quiet)
echo "#ts# (\"U2__DSID_1\", \"$dataset\"),"
dataset=$(omero obj new Dataset name='U2-NoProj--Dset02' --quiet)
echo "#ts# (\"U2__DSID_2\", \"$dataset\"),"
