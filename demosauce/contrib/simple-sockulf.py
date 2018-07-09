#!/usr/bin/python2
# this is a dumbed down version of sockulf to show how to feed demosauce
# with songs and metadata. command_nextsong is where all the magic happens

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# 'maep' on ircnet wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return
# ----------------------------------------------------------------------------

import os, socket, random, pickle, re, sys, signal, subprocess as sp
from optparse import OptionParser

def gv(data, exp):
    r = re.compile(exp)
    try:
        return r.search(data).group(1)
    except:
        return ''

def scan(path):
    program = '../dscan'
    p = sp.Popen([program, '-r', path], stdout = sp.PIPE)
    output = p.communicate()[0]
    if p.returncode != 0:
        return (False, '', '', '0')
    artist = gv(output, r'artist:(.*)')
    title = gv(output, r'title:(.*)')
    gain = gv(output, r'replaygain:(-?\d*\.?\d+)')
    print path, artist, title, gain, "dB"
    return (True, title, artist, gain)

# a very simple database
class songDb(object):
    def __init__(self, path):
        self.dict = {}
        self.file = path
        print 'loading db ', path
        if os.path.isfile(path):
            self.dict = pickle.load(open(path, 'rb'))

    def save(self):
        pickle.dump(self.dict, open(self.file, 'wb'), 2)

    def add(self, path):
        if not path in self.dict:
            self.dict[path] = scan(path)
        return self.dict[path][0]

    def get(self, path):
        return self.dict[path]

# a very primitive dj
class djDerp(object):
    def __init__(self, root):
        self.pos = 0
        self.db = songDb('sockulf.db')
        self.playlist = self.crawldir(root)
        self.db.save()
        random.shuffle(self.playlist)
        print len(self.playlist), 'songs in playlist'
        if len(self.playlist) == 0:
            print 'directory is empty, nothing to play'
            exit(1)

    def crawldir(self, root):
        pathlist = []
        print 'scanning files'
        for dir, dirs, files in os.walk(root):
            for f in sorted(files):
                path = os.path.join(dir, f)
                if self.db.add(path):
                    pathlist.append(path)
        return pathlist

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
        self.COMMANDS = {'NEXTSONG': self.command_nextsong}
        self.dj = dj
        self.host = host
        self.port = port
        self.timeout = timeout
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind((self.host, self.port))
        self.listener.settimeout(timeout)

    def listen(self):
        print 'listening on %s:%s' % (self.host, self.port)
        while True:
            self.listener.listen(1)
            self.conn, self.addr = self.listener.accept()
            data = self.conn.recv(1024).strip()
            if not data:
                continue
            if data in self.COMMANDS.keys():
                result = self.COMMANDS[data]()
                self.conn.send(result)
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
            l.append('%s=%s' % (k, v))
        return '\n'.join(l)

def signal_handler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    usage = 'usage %prog [options] path'
    parser = OptionParser(usage)
    parser.add_option('-p', '--port', dest='port', default='32167', help='on which port to listen')
    parser.add_option('-i', '--ip', dest='ip', default='127.0.0.1', help='to what address to bind')

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('you must specify a path')

    signal.signal(signal.SIGINT, signal_handler)

    HOST = options.ip
    PORT = int(options.port)
    TIMEOUT = None

    server = pyWhisperer(djDerp(args[0]), HOST, PORT, TIMEOUT)
    print 'press ctrl-c to quit'
    server.listen()

