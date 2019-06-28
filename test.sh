#!/usr/bin/env bash

#
# Curl /exec/<plug>/<command> a bunch of times, while
# a background process is deploying new versions.
#
# The plug tries to check its integrity before
# producing its output.
#

while :; do ./bump-plug.sh foo >/dev/null; done&
daemon=$!
trap 'kill $daemon' EXIT

for _ in {1..100}; do
    curl http://localhost:5000/exec/foo/main
done
