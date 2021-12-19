# run 'make' to build
# run 'make clean' to clear build artifacts
# run 'make clobber' to clear artifacts incl. libraries

include makefile.conf
vpath %.c  src
vpath %.a  libs
vpath %.so libs

PKG_LIBS  = libavcodec libavformat libavutil libswresample vorbisfile
CPPFLAGS += -Ilibs/replaygain -Ilibs/bass -Ilibs/openmpt -Ilibs/hively
CFLAGS   += -std=c11 -pthread $(shell pkg-config --cflags $(PKG_LIBS))
LDFLAGS  += -Llibs -lm -lz -lopenmpt -lhively $(shell pkg-config --libs $(PKG_LIBS))
LIBS	 += libreplaygain.a libopenmpt.a libhively.a

DEMOSAUCE_SRC  += demosauce.c cast.c decoder.c ffdecoder.c omptdecoder.c hvldecoder.c log.c settings.c stream.c util.c
DEMOSAUCE_LINK += -lmp3lame $(shell pkg-config --libs shout)
DEMOSAUCE_OBJ   = $(patsubst %.c,obj/%.o, $(DEMOSAUCE_SRC))

DSCAN_SRC  += dscan.c decoder.c ffdecoder.c omptdecoder.c hvldecoder.c log.c stream.c util.c
DSCAN_LINK += -lreplaygain $(shell pkg-config --libs libchromaprint)
DSCAN_OBJ   = $(patsubst %.c,obj/%.o, $(DSCAN_SRC))

all: demosauce dscan

demosauce: $(LIBS) obj $(DEMOSAUCE_OBJ)
	$(CXX) $(DEMOSAUCE_OBJ) $(LDFLAGS) $(DEMOSAUCE_LINK) -o demosauce

dscan: $(LIBS) obj $(DSCAN_OBJ)
	$(CXX) $(DSCAN_OBJ) $(LDFLAGS) $(DSCAN_LINK) -o dscan

obj/%.o: %.c
	$(CC) -Wall $(CFLAGS) $(CPPFLAGS) -c $< -o $@

obj:
	mkdir -p $@

clean:
	rm -f demosauce dscan
	rm -rf obj

clobber: clean
	find libs -name "*.a" -o -name "*.so" -o -name "*.o" | xargs rm

libbass.so:
	cd libs/bass; ./getbass.sh
	cp libs/bass/libbass.so libs/libbass.so

libreplaygain.a:
	$(MAKE) -C libs/replaygain
	cp libs/replaygain/libreplaygain.a libs/

libopenmpt.a:
	$(MAKE) -C libs/openmpt SHARED_LIB=0 EXAMPLES=0 OPENMPT123=0 TEST=0 -j4
	cp libs/openmpt/bin/libopenmpt.a libs/

libhively.a:
	$(MAKE) -C libs/hively
	cp libs/hively/libhively.a libs/
