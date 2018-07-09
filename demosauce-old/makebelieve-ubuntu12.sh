#!/bin/sh
#generated build script
CFLAGS='-Wall -O2 -s -I/usr/local/include -DENABLE_BASS'
compile(){
	echo g++ $@
	if ! g++ $@; then exit 1; fi
}
rm -f demosauce scan ladspainfo
cd src
compile $CFLAGS -c logror.cpp
compile $CFLAGS -I../bass -c libbass.c
compile $CFLAGS   -I../bass -c basssource.cpp
compile $CFLAGS -I../ffmpeg -c avsource.cpp
compile $CFLAGS -DBUILD_ID=`git describe --always` -c demosauce.cpp
compile $CFLAGS -pthread   -I. -c shoutcast.cpp
compile $CFLAGS -DBUILD_ID=`git describe --always`   -I../libreplaygain -c scan.cpp
compile $CFLAGS -c settings.cpp
compile $CFLAGS   -c convert.cpp
compile $CFLAGS -c effects.cpp
compile $CFLAGS -c sockets.cpp
compile $CFLAGS scan.o avsource.o effects.o logror.o convert.o libbass.o basssource.o -L../libreplaygain -lreplaygain -lboost_system-mt -lboost_filesystem-mt -lid3tag -ldl -L../ffmpeg -pthread -lavformat -lavcodec -lavutil -lsamplerate -L/usr/local/lib -lz   -o scan
compile $CFLAGS settings.o demosauce.o avsource.o convert.o effects.o logror.o sockets.o shoutcast.o libbass.o basssource.o  -lboost_system-mt -lboost_thread-mt -lboost_filesystem-mt -lboost_program_options-mt -lid3tag -ldl -L../ffmpeg -pthread -lavformat -lavcodec -lavutil -lshout -lsamplerate -L/usr/local/lib -lz   -ldl -lm   -L/usr/lib -licui18n -licuuc -licudata  -ldl -lm    -o demosauce

rm -f *.o
