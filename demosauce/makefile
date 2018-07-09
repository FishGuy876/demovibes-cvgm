include makefile.conf
vpath %.c  src
vpath %.so libs

PKG_LIBS  = libavcodec libavformat libavutil libswresample
CPPFLAGS += -Ilibs/replaygain -Ilibs/bass -Ilibs/openmpt -Ilibs/hively
CFLAGS   += -std=c11 -pthread $(shell pkg-config --cflags $(PKG_LIBS))
LDFLAGS  += -Llibs -lm -lopenmpt -lhively -pthread -Wl,-rpath='$$ORIGIN/libs' $(shell pkg-config --libs $(PKG_LIBS))
LIBS	 += libreplaygain.so libopenmpt.so libhively.so

DEMOSAUCE_SRC  += demosauce.c cast.c decoder.c ffdecoder.c omptdecoder.c hvldecoder.c log.c settings.c stream.c util.c
DEMOSAUCE_LINK += -lmp3lame $(shell pkg-config --libs shout)
DEMOSAUCE_OBJ   = $(patsubst %.c,obj/%.o, $(DEMOSAUCE_SRC))

DSCAN_SRC  += dscan.c decoder.c ffdecoder.c omptdecoder.c hvldecoder.c log.c stream.c util.c
DSCAN_LINK += -lreplaygain $(shell pkg-config --libs libchromaprint)
DSCAN_OBJ   = $(patsubst %.c,obj/%.o, $(DSCAN_SRC))

all: demosauce dscan

demosauce: $(LIBS) obj $(DEMOSAUCE_OBJ)
	$(CC) $(DEMOSAUCE_OBJ) $(LDFLAGS) $(DEMOSAUCE_LINK) -o demosauce

dscan: $(LIBS) obj $(DSCAN_OBJ)
	$(CC) $(DSCAN_OBJ) $(LDFLAGS) $(DSCAN_LINK) -o dscan

obj/%.o: %.c
	$(CC) -Wall $(CFLAGS) $(CPPFLAGS) -c $< -o $@

obj:
	mkdir -p $@

clean:
	rm -f demosauce dscan
	rm -rf obj

clobber: clean
	cd libs; rm -f $(LIBS)

libbass.so:
	cd libs/bass; ./getbass.sh
	ln -fs bass/libbass.so libs/libbass.so

libreplaygain.so:
	$(MAKE) -C libs/replaygain
	ln -fs replaygain/libreplaygain.so libs/libreplaygain.so

libopenmpt.so:
	$(MAKE) -C libs/openmpt STATIC_LIB=0 EXAMPLES=0 OPENMPT123=0 TEST=0 -j4
	ln -fs openmpt/bin/libopenmpt.so.0 libs/libopenmpt.so
	ln -fs openmpt/bin/libopenmpt.so.0 libs/libopenmpt.so.0

libhively.so:
	$(MAKE) -C libs/hively
	ln -fs hively/libhively.so libs/libhively.so
