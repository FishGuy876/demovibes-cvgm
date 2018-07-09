#!/usr/bin/env python

from urllib2 import urlopen
from socket import inet_aton, inet_ntoa
import struct, sys, os, logging
from ip2cc import cc2name

logger = logging.getLogger(__name__)


class IPTree(object):

    value_length = 2

    def __init__(self):
        self._tree = ['\x00'*self.value_length]*256

    def add(self, start, end, value):
        self._set_range(self._tree, [int(n) for n in start.split('.')],
                        [int(n) for n in end.split('.')], value)

    def _get_sub_tree(self, tree, idx):
        if isinstance(tree[idx], str):
            tree[idx] = [tree[idx]]*256
        return tree[idx]

    def _set_range(self, tree, start, end, value):
        assert isinstance(tree, list)
        assert len(start)==len(end)
        if start[0]==end[0]:
            if start[1:]==[0]*(len(start)-1) and end[1:]==[255]*(len(end)-1):
                tree[start[0]] = value
            else:
                self._set_range(self._get_sub_tree(tree, start[0]),
                                start[1:], end[1:], value)
        elif len(start)==1:
            for idx in range(start[0], end[0]+1):
                tree[idx] = value
        else:
            if start[1:]==[0]*(len(start)-1):
                tree[start[0]] = value
            else:
                self._set_range(self._get_sub_tree(tree, start[0]),
                                start[1:], [255]*(len(start)-1), value)
            for idx in range(start[0]+1, end[0]):
                tree[idx] = value
            if end[1:]==[255]*(len(end)-1):
                tree[end[0]] = value
            else:
                self._set_range(self._get_sub_tree(tree, end[0]),
                                [0]*(len(end)-1), end[1:], value)

    def optimize(self, tree=None):
        if tree is None:
            tree = self._tree
        for idx in range(256):
            node = tree[idx]
            if isinstance(node, list):
                assert len(node)==256
                if node==[node[0]]*256:
                    tree[idx] = node[0]
                else:
                    self.optimize(node)

    def dump(self, offset=0, tree=None):
        if tree is None:
            tree = self._tree
        assert isinstance(tree, list)
        import struct
        offsets = []
        subtrees = []
        end = offset+256*(2+self.value_length)
        for node in tree:
            if isinstance(node, str):
                if len(node)>self.value_length:
                    logger.warning('Value %r too long, truncated', node)
                offsets.append('\xFF\xFF%*s' % (self.value_length, node))
            else:
                offsets.append(struct.pack('!I', end) + \
                                    '\x00'*(self.value_length-2))
                subtrees.append(self.dump(end, node))
                end += len(subtrees[-1])
        assert len(''.join(offsets))==256*(2+self.value_length), (len(''.join(offsets)), 256*(2+self.value_length))
        result = ''.join(offsets+subtrees)
        assert len(result)==end-offset
        return result


class CountryByIPTree(IPTree):

    # Change it to the closest mirror. Official are:
    #   ftp://ftp.ripe.net/pub/stats/
    #   ftp://ftp.arin.net/pub/stats/
    #   ftp://ftp.apnic.net/pub/stats/
    #   ftp://ftp.lacnic.net/pub/stats/
    url_template = 'ftp://ftp.ripe.net/pub/stats/%s/delegated-%s-latest'
    sources = {}
    for name in ('ripencc', 'apnic', 'lacnic', 'afrinic'):
        sources[name] = url_template % (name, name)

    def fetch(self):
        for name, source in self.sources.items():
            logger.info('Fetching from %r', source)
            fp = urlopen(source)
            for line in iter(fp.readline, ''):
                parts = line.strip().split('|')
                if len(parts)==7 and parts[2]=='ipv4' and \
                        parts[6] in ('allocated', 'assigned') and \
                        name==parts[0]:
                    first = parts[3]
                    first_int = struct.unpack('!I', inet_aton(first))[0]
                    last_int = first_int+int(parts[4])-1
                    last = inet_ntoa(struct.pack('!I', last_int))
                    try:
                        self.add(first, last, parts[1].upper())
                    except ValueError:
                        pass

    def add(self, start, end, cc):
        if not cc in cc2name:
            logger.warning('Unknown country code %r\n', cc)
        IPTree.add(self, start, end, cc)


def create_file(db_file):
    logging.basicConfig(level=logging.INFO)
    tree = CountryByIPTree()
    tree.fetch()
    tree.optimize()
    db = open(db_file+'.new', 'wb')
    db.write(tree.dump())
    db.close()
    os.rename(db_file+'.new', db_file)

if __name__=='__main__':
    db_file = os.path.join(os.path.dirname(sys.argv[0]), 'ip2cc.db')
    create_file(db_file)
