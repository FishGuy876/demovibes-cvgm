#!/bin/sh

# runs scan on a bunch of files that cause problems in the past.
# build with ASan to find memory bugs

for FILE in $@; do
    ./dscan $FILE -cr || echo "test failed"
done
