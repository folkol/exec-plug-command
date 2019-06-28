#!/usr/bin/env bash

#
# Creates and uploads version of plug <NAME>.
#
# (Expects aws-cli to be configured.)
#

BUCKET=folkol.com

if [ ! $# -eq 1 ]; then
    echo 'usage: ./bump-plug.sh NAME' >&2
    exit 1
fi

name=$1
tmpdir=$(mktemp -d)
trap 'rm -r $tmpdir' EXIT
cd "$tmpdir" || exit 1

version=$RANDOM
for i in {1..100}; do
    echo "VERSION=$version" >module$i.py
    echo "import module$i" >>main.py
    echo "assert module$i.VERSION == $version, 'module$i seems broken'" >>main.py
done

echo "print('Looks good to me!')" >>main.py

zip "$name.zip" -- *
aws s3 cp "$name.zip" "s3://$BUCKET/$name.zip"
