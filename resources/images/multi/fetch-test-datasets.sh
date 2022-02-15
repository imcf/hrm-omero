#!/bin/bash

set -e

cd "$(dirname "$0")"

if [ -d "zenodo" ]; then
    echo "Found directory 'zenodo', not re-downloading files."
    exit 0
fi

mkdir "zenodo"
cd "zenodo"

while read -r URI; do
    wget "$URI"
done <"../zenodo-links.txt"

for ZIPFILE in *.zip; do
    unzip "$ZIPFILE"
done
