#!/usr/bin/python
# this is a dumbed down version of sockulf to show how to feed demosauce
# with songs and metadata. command_nextsong is where all the magic happens

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# 'maep' on ircnet wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------

import os, socket, random
import cPickle
import re, sys, signal
import subprocess

def gv(data, exp):
    r = re.compile(exp)
    try:
        v = r.search(data).group(1)
    except:
        v = ""
    return v

def scan(file):
    program = '../scan'
    p = subprocess.Popen([program, file], stdout = subprocess.PIPE)
    output = p.communicate()[0]
    if p.returncode != 0:
        return (False, "", "", "0")
    artist = gv(output, r'artist:(.*)')
    title = gv(output, r'title:(.*)')
    gain = gv(output, r'replaygain:(-?\d*\.?\d+)')
    print file, artist, title, gain, "dB"
    return (True, title, artist, gain)
    
# a very simple database
class songDb(object):
    def __init__(self, file):
        self.dict = {}
        self.file = file
        print 'loading db ', file
        if os.path.isfile(file):
            self.dict = cPickle.load(open(file))

    def save(self):
        cPickle.dump(self.dict, open(self.file, 'w'))
    
    def add(self, file):
        if not file in self.dict:
            self.dict[file] = scan(file)
        return self.dict[file][0]

    def get(self, file):
        return self.dict[file]

# a very primitive dj
class djDerp(object):
    def __init__(self, root):
        self.pos = 0
        self.db = songDb(os.path.join(os.path.expanduser('~'), 'sockulf.db'))
        self.playlist = self.crawldir(root)
        self.db.save()
        random.shuffle(self.playlist)
        print len(self.playlist), 'songs in playlist'
        if len(self.playlist) == 0:
            print 'directory is empty, nothing to play'
            exit(1)

    def crawldir(self, root):
        list = []
        print 'scanning files'
        for dir, dirs, files in os.walk(root):
            for file in files:
                path = os.path.join(dir, file)
                if self.db.add(path):
                    list.append(path)
        return list

    # returns filename, title, artist, gain
    def nextsong(self):
        self.pos += 1
        if self.pos >= len(self.playlist):
            random.shuffle(self.playlist)
            self.pos = 0
        file = self.playlist[self.pos]
        foo, title, artist, gain = self.db.get(file)
        if not title:
            title = os.path.basename(file)
        return file, artist, title, gain

# handles communication with demosauce
class pyWhisperer(object):
    def __init__(self, dj, host, port, timeout):
        self.COMMANDS = {
            'NEXTSONG': self.command_nextsong,
        }
        self.dj = dj
        self.host = host
        self.port = port
        self.timeout = timeout
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind((self.host, self.port))
        self.listener.settimeout(timeout)

    def listen(self):
        print "listening on %s:%s" % (self.host, self.port)
        while True:
            self.listener.listen(1)
            self.conn, self.addr = self.listener.accept()
            data = self.conn.recv(1024)
            i = 0
            if data:
                data = data.strip()
                if data in self.COMMANDS.keys():
                    result = self.COMMANDS[data]()
                    while i < len(result):
                        i = i + self.conn.send(result)
            self.conn.close()
        self.listener.close()

    def command_nextsong(self):
        (path, artist, title, gain) = self.dj.nextsong()
        data = {
            'path': path,
            'artist': artist,
            'title': title,
            'gain': gain,
        }
        print 'next song:', path
        return self.encode(data)

    def encode(self, data):
        l = []
        for k, v in data.items():
            l.append("%s=%s" % (k, v))
        return "\n".join(l)

def signal_handler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    from optparse import OptionParser
    usage = "usage %prog [options] path"
    parser = OptionParser(usage)
    parser.add_option("-p", "--port", dest="port", default="32167", help = "Which port to listen to")
    parser.add_option("-i", "--ip", dest="ip", default="127.0.0.1", help="What IP address to bind to")

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("you must specify a path")

    signal.signal(signal.SIGINT, signal_handler)
    
    HOST = options.ip
    PORT = int(options.port)
    TIMEOUT = None

    server = pyWhisperer(djDerp(args[0]), HOST, PORT, TIMEOUT)
    print "press ctrl-c to quit"
    server.listen()

