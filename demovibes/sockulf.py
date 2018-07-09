#!/usr/bin/env python

import socket
import logging
import queuefetcher

from django.core.management import setup_environ
import settings

setup_environ(settings)
max_length = getattr(settings, 'MAX_SONG_LENGTH', False)

Log = logging.getLogger("Sockulf")

class pyWhisperer(object):
    def __init__(self, host, port, timeout):
        Log.debug("Initiating listener with values HOST='%s', PORT='%s'." % (host, port))
        self.COMMANDS = {
            'GETSONG': self.command_getsong,
            'GETMETA': self.command_getmeta,
            'DIE': self.command_die,
            'GETTITLE': self.command_title,
            'GETARTIST': self.command_artist,
            'MEMDUMP': self.command_memdump,
            'GETGAIN': self.command_getgain,
            'GETLOOP': self.command_getloop,
            'NEXTSONG': self.command_nextsong,
        }
        self.host = host
        self.port = port
        self.encode = self.encode_newline
        self.player = queuefetcher.song_finder()
        self.running = True
        self.timeout = timeout
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.host, self.port))
        self.listener.settimeout(timeout)

    def listen(self):
        Log.debug("Starting loop")
        while self.running:
                self.listener.listen(1)
                Log.debug("Listening for connections..")
                self.conn, self.addr = self.listener.accept()
                Log.debug("Accepted connection from %s" % self.addr[0])
                data = self.conn.recv(1024)
                i = 0
                if data:
                        data = data.strip()
                        Log.debug("Got message : %s" % data)
                        if data in self.COMMANDS.keys():
                                result = self.COMMANDS[data]()
                                Log.debug("Returning data : %s" % result)
                                while i < len(result):
                                        i = i + self.conn.send(result)
                        else:
                                Log.debug("Unknown command!")
                else:
                        Log.debug("No data received")
                Log.debug("Closing connection")
                self.conn.close()
        Log.debug("Closing down listener")
        self.listener.close()

    def encode_newline(self, data):
        l = []
        for k, v in data.items():
            l.append("%s=%s" % (k, v))
        return "\n".join(l)

    def command_nextsong(self):
        data = {
            'path': self.command_getsong(),
            'artist': self.command_artist(),
            'title': self.command_title(),
            'gain': self.command_getgain(),
        }
        moredata = self.player.song.get_playoptions()
        data.update(moredata)
        return self.encode(data)

    def command_artist(self):
        return self.player.song.artist().encode("utf-8")

    def command_title(self):
        return self.player.song.title.encode("utf-8")

    def command_getsong(self):
        return self.player.get_next_song()

    def command_getloop(self):
        if max_length and self.player.song.song_length > max_length:
            return str(max_length)
        return str(self.player.song.loopfade_time)

    def command_getgain(self):
        return str(self.player.song.replay_gain)

    def command_getmeta(self):
        return self.player.get_metadata()

    def command_memdump(self):
        try:
            from meliae import scanner
            scanner.dump_all_objects("sockulf.dump")
            return "Memory dumped!"
        except:
            return "Could not dump memory! (meliae not installed?)"

    def command_die(self):
        self.running = False
        return "Goodbye cruel world!"

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", default="32167", help = "Which port to listen to")
    parser.add_option("-i", "--ip", dest="ip", default="127.0.0.1", help="What IP address to bind to")
    (options, args) = parser.parse_args()

    HOST = options.ip
    PORT = int(options.port)
    TIMEOUT = None

    logging.basicConfig(level=logging.WARNING)
    Log.setLevel(logging.INFO)
    server = pyWhisperer(HOST, PORT, TIMEOUT)
    server.listen()

