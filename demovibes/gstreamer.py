#!/usr/bin/python

import pygst
pygst.require("0.10")
import gst
import gtk

import queuefetcher

class Main:
    def __init__(self, config):
        self.c = config
        self.player = queuefetcher.song_finder()

        input_filter = config.get("gstreamer", "input_filter")
        output_filter = config.get("gstreamer", "output_filter")

        self.pipeline = self.make_pipeline(input_filter, output_filter)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        self.playnext()

    def getfile(self):
        return self.player.get_next_song()

    def set_properties_from_config(self, element, section):
        try:
            items = self.c.items(section)
        except:
            return False
        for k, v in items:
            element.set_property(k, v.isdigit() and int(v) or v)
        return True


    def make_pipeline(self, input_filter, output_filter):
        path = []
        pipeline = gst.Pipeline("mypipeline")

        audiosrc = gst.element_factory_make("filesrc", "file-source")
        path.append(audiosrc)

        decoder = gst.element_factory_make(input_filter, None)
        self.set_properties_from_config(decoder, input_filter)
        path.append(decoder)

        #Convert audio data to something ready for shoutcast
        audioconvert = gst.element_factory_make("audioconvert", None)
        audioresample = gst.element_factory_make("audioresample", None)

        encoder = gst.element_factory_make(output_filter, None)
        self.set_properties_from_config(encoder, output_filter)

        queue = gst.element_factory_make("queue", None)
        queue.set_property("min-threshold-buffers", 10)

        path.append(audioconvert)
        path.append(audioresample)
        path.append(encoder)
        path.append(queue)

        shout2send = gst.element_factory_make("shout2send", "streamer")
        self.set_properties_from_config(shout2send, "shoutcast")
        path.append(shout2send)

        pipeline.add(*path)
        gst.element_link_many(*path)

        return pipeline

    def stop_stream(self):
        self.pipeline.set_state(gst.STATE_READY)

    def start_stream(self):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def playnext(self):
        self.stop_stream()

        nextfile = self.getfile()
        print "Playing", nextfile
        src = self.pipeline.get_by_name("file-source")
        src.set_property("location", nextfile)

        self.start_stream()

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.playnext()
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug



import ConfigParser

c = ConfigParser.SafeConfigParser()
try:
    c.read("gstreamer.ini")
    c.get("gstreamer", "input_filter")
except:
    print "Could not read config file. Writing some defaults to gstreamer.ini"
    c.add_section("shoutcast")
    c.add_section("gstreamer")
    c.set("shoutcast", "mount", raw_input("Input icecast mount point: "))
    c.set("shoutcast", "password", raw_input("Input icecast streamer password: "))
    c.set("gstreamer", "input_filter", "mad")
    c.set("gstreamer", "output_filter", "lame")
    f = open("gstreamer.ini", "wb")
    c.write(f)
    f.close()
    print "Okay, done. Continuing startup"


start=Main(c)

gtk.main()
