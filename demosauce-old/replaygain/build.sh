#!/bin/sh
OUTPUT='libreplaygain.a'

gcc -Wall -std=c99 -O3 -ffast-math -c gain_analysis.c replay_gain.c

if test $? -eq 0; then
	rm -f $OUTPUT
	ar rs $OUTPUT *.o
	rm *.o
fi
