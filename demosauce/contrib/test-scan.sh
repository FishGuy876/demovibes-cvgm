#!/bin/sh

# runs scan on a bunch of files that caused problems in the past.
# build with ASan to find memory bugs

for FILE in "$@"; do
    echo "$FILE"
    ./dscan "$FILE" -cr || echo "test failed"
done
