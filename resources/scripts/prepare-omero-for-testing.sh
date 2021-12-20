#!/bin/bash

function extract_omero_id() {
    # parse the ID from the output of an `omero` command, e.g. like:
    # "Added group SYS Test HRM-OMERO 1 (id=9) with permissions rwra--"
    sed 's/.*(id=\([0-9]*\)).*/\1/'
}

function random_password() {
    tr -dc a-zA-Z0-9 </dev/urandom | head -c 16
    echo ""
}

function omero_group_add() {
    GIDCOUNT=$((GIDCOUNT + 1))
    . "$SEEDS" # (re-) read the GIDs, UIDs, passwords
    if grep -qs "^GID_${GIDCOUNT}=" "$SEEDS"; then
        echo "Using pre-defined group ID!"
        return
    fi
    ID_STR=$(omero group add --type read-annotate "$1" --quiet 2>&1)
    RETVAL=$?
    if [ "$RETVAL" -gt 0 ]; then
        if [ "$RETVAL" -eq 3 ]; then
            echo "Using existing group!"
        else
            echo " ---- STOPPING ---- "
            exit $RETVAL
        fi
    fi
    ID=$(echo "$ID_STR" | extract_omero_id)
    echo "GID_${GIDCOUNT}=$ID" | tee -a "$SEEDS"
    echo "GID_${GIDCOUNT}: $ID" >>"$YAML"
    . "$SEEDS" # (re-) read the GIDs, UIDs, passwords
}

function omero_user_add() {
    UIDCOUNT=$((UIDCOUNT + 1))
    . "$SEEDS" # (re-) read the GIDs, UIDs, passwords
    if grep -qs "^UID_${UIDCOUNT}=" "$SEEDS"; then
        echo "Using pre-defined user ID!"
        return
    fi
    PWD_STR="^U${UIDCOUNT}_PW"
    if grep -qs "$PWD_STR" "$SEEDS"; then
        echo "Using pre-defined password!"
        eval "USER_PW=$(grep "$PWD_STR" "$SEEDS" | cut -d '=' -f 2)"
    else
        USER_PW=$(random_password)
    fi
    ID_STR=$(omero user add "$1" "$2" "$3" --userpassword "$USER_PW" --group-id "$4" --quiet 2>&1)
    RETVAL=$?
    if [ "$RETVAL" -gt 0 ]; then
        if [ "$RETVAL" -eq 3 ]; then
            echo "Using existing user!"
            echo "Please edit '$SEEDS' in case the password for user '$1' doesnt match!"
            USER_PW=""
        else
            echo " ---- STOPPING ---- "
            exit $RETVAL
        fi
    fi
    ID=$(echo "$ID_STR" | extract_omero_id)
    echo "### OMERO username: $1" | tee -a "$SEEDS"
    echo "UID_${UIDCOUNT}=$ID" | tee -a "$SEEDS"
    echo "UID_${UIDCOUNT}: $ID" >>"$YAML"
    if [ -z "$USER_PW" ]; then
        PFX="# "
    fi
    echo "${PFX}U${UIDCOUNT}_PW=$USER_PW" >>"$SEEDS"
    . "$SEEDS" # (re-) read the GIDs, UIDs, passwords
}

function prepare_omero_admin_connection() {
    . "$SEEDS" # (re-) read the GIDs, UIDs, passwords

    if [ -z "$SERVER" ]; then
        read -p "Address of your OMERO server: [local-omero] " SERVER
        SERVER=${SERVER:-local-omero}
        echo "SERVER=$SERVER" >>"$SEEDS"
    fi

    if [ -z "$OMERO_USER" ]; then
        read -p "Username: [root] " OMERO_USER
        OMERO_USER=${OMERO_USER:-root}
        echo "OMERO_USER=$OMERO_USER" >>"$SEEDS"
    fi

    if [ -z "$OMERO_PASSWORD" ]; then
        read -p "Password: " OMERO_PASSWORD
        OMERO_PASSWORD=${OMERO_PASSWORD:-omero_root_password}
        echo "OMERO_PASSWORD=$OMERO_PASSWORD" >>"$SEEDS"
    fi
}

###############################################################################

cat - <<EOF

    ***************************************************************************
    **                              WARNING                                  **
    ***************************************************************************
    **  NEVER run this script against a PRODUCTION server, this is purely    **
    **  meant to set up a defined environment for testing the HRM-OMERO      **
    **  connector against an actual OMERO (e.g. in a development container)  **
    **                                                                       **
    **  This has been tested against OMERO 5.6.3 - use with caution on any   **
    **  other version and test in an isolated environment (VM/container/...) **
    ***************************************************************************

    Press <Enter> to continue or <Ctrl>+<C> to abort!
EOF
read

GIDCOUNT=0
UIDCOUNT=0

SEEDS=${1:-$(mktemp --suffix=.inc.sh)}
YAML=${2:-$(mktemp --suffix=.yml)}

GNAME_1="SYS Test HRM-OMERO 1"
GNAME_2="SYS Test HRM-OMERO 2"
TESTIMAGE="$(dirname "$0")/../../resources/images/3ch-dapi-pha-atub.ics"

echo "Using seeds file '$SEEDS' for reading and storing IDs etc."
if ! [ -f "$SEEDS" ]; then
    echo "# preparation script values for testing HRM-OMERO" >"$SEEDS"
    echo "# created at $(date "+%F %H:%m:%S")" >>"$SEEDS"
fi

prepare_omero_admin_connection

. "$SEEDS" # re-read the GIDs, UIDs, passwords

# log in with an account that can create users and groups:
omero logout
omero login --server "$SERVER" --user "$OMERO_USER" --password "$OMERO_PASSWORD"

echo "Creating two test groups..."
omero_group_add "$GNAME_1"
omero_group_add "$GNAME_2"

echo "Creating two users, adding them to the first group..."
omero_user_add "hrm-test-01" "Test-01" "HRM-OMERO" "$GID_1"
omero_user_add "hrm-test-02" "Test-02" "HRM-OMERO" "$GID_1"

echo "Adding the users to the second group..."
omero group adduser --id "$GID_2" --user-id "$UID_1" --quiet
omero group adduser --id "$GID_2" --user-id "$UID_2" --quiet

echo " ----------- processing steps for first OMERO user ----------- "

echo "Reconnecting using the newly created user..."
omero logout
omero login -u "hrm-test-01" -w "$U1_PW" --server "$SERVER" --quiet

echo "Creating a project-dataset-tree..."
project=$(omero obj new Project name='Proj01' --quiet)
dataset=$(omero obj new Dataset name='Proj01--Dset01' --quiet)
omero obj new ProjectDatasetLink parent="$project" child="$dataset" --quiet
echo "U1__PID_1: $project" | tee -a "$YAML"
echo "U1__PID_1__DSID_1: $dataset" | tee -a "$YAML"

echo "Importing a test image there..."
image=$(omero import -d "$dataset" "$TESTIMAGE" --quiet)
echo "U1__IID_1: $image" | tee -a "$YAML"

echo "Creating another dataset in that project to be used as an upload target..."
dataset=$(omero obj new Dataset name='upload-target' --quiet)
omero obj new ProjectDatasetLink parent="$project" child="$dataset" --quiet
echo "U1__PID_1__DSID_2: $dataset" | tee -a "$YAML"

echo "Creating a dataset without a project (top-level)..."
dataset=$(omero obj new Dataset name='NoProj--Dset01' --quiet)
echo "U1__DSID_1: $dataset" | tee -a "$YAML"

echo " ----------- processing steps for second OMERO user ----------- "

echo "Reconnecting using the second user..."
omero logout
omero login -u "hrm-test-02" -w "$U2_PW" --server "$SERVER" --quiet

echo "Creating a project-dataset-tree..."
project=$(omero obj new Project name='U2-Proj01' --quiet)
dataset=$(omero obj new Dataset name='U2-Proj01--Dset01' --quiet)
omero obj new ProjectDatasetLink parent="$project" child="$dataset" --quiet
echo "U2__PID_1: $project" | tee -a "$YAML"
echo "U2__PID_1__DSID_1: $dataset" | tee -a "$YAML"
dataset=$(omero obj new Dataset name='U2-Proj01--Dset02' --quiet)
omero obj new ProjectDatasetLink parent="$project" child="$dataset" --quiet
echo "U2__PID_1__DSID_2: $dataset" | tee -a "$YAML"

echo "Creating some datasets without a project (top-level)..."
dataset=$(omero obj new Dataset name='U2-NoProj--Dset01' --quiet)
echo "U2__DSID_1: $dataset" | tee -a "$YAML"
dataset=$(omero obj new Dataset name='U2-NoProj--Dset02' --quiet)
echo "U2__DSID_2: $dataset" | tee -a "$YAML"

echo " ----------- done - see YAML summary from [$YAML] below ----------- "
cat "$YAML"
