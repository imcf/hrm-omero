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
G1_ID=9
G2_ID=903

# generate random 16-char passwords using letters (upper- and lower-case) and digits
U1_PW=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 16 ; echo '')
U2_PW=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 16 ; echo '')

# create two users, add them to the first group:
omero user add "hrm-test-01" Test-01 HRM-OMERO --userpassword "$U1_PW" --group-id "$G1_ID"
omero user add "hrm-test-02" Test-02 HRM-OMERO --userpassword "$U2_PW" --group-id "$G1_ID"

# again, make sure to parse the newly created user IDs from the output similar to this:
# ---
# Added user hrm-test-01 (id=5810) with password
# ---
U1_ID=5810
U2_ID=5811

# add the users to the second group:
omero group adduser --id "$G2_ID" --user-id "$U1_ID"
omero group adduser --id "$G2_ID" --user-id "$U2_ID"

# reconnect using the newly created user:
omero logout
omero login -u "hrm-test-01" -w "$U1_PW"

# create a project-dataset-tree:
project=$(omero obj new Project name='Proj01')
dataset=$(omero obj new Dataset name='Proj01--Dset01')
omero obj new ProjectDatasetLink parent="$project" child="$dataset"

# create a dataset without a project (top-level):
project=$(omero obj new Dataset name='NoProj--Dset01')