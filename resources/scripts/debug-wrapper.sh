#!/bin/sh

# This is a thin wrapper that can be used around the actual connector's
# executable by renaming that one to "ome_hrm.py.real" and putting this script
# in its original place. Contact the developers in case you need help with this.

BASEDIR=$(dirname "$0")

{
    echo "======================= ome_hrm debug wrapper ======================="
    echo "$BASEDIR"
    echo "PYTHONPATH: $PYTHONPATH"
    echo "JAVA_HOME: $JAVA_HOME"
    echo "----"
    env
    echo "----"
    "$BASEDIR"/ome_hrm.py.real "$@"
    echo "---------------------------------------------------------------------"
} >>/tmp/ome_hrm_debug.log 2>&1
