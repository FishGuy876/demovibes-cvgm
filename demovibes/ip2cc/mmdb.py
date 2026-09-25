"""
Minimal reader for MaxMind DB (.mmdb) country databases, such as DB-IP's
free "IP to Country Lite" (https://db-ip.com/db/download/ip-to-country-lite).

Replaces the old ip2cc tree format, which ipcountry.db has not been in since
it was swapped for a DB-IP file. Only what a country lookup needs is here:
the search tree, and a data decoder for the record it lands on. Handles IPv4
and IPv6. Pure Python, runs on 2.7 and 3.x, no packages to install.

Usage matches ip2cc.CountryByIP: db[ip] returns an upper-case ISO 3166-1
alpha-2 code, or raises KeyError if the address is not in the database.

Format spec: https://maxmind.github.io/MaxMind-DB/
"""

import mmap
import socket
import struct

METADATA_MARKER = b'\xab\xcd\xefMaxMind.com'
DATA_SECTION_SEPARATOR = 16


class InvalidDatabaseError(Exception):
    pass


class _Decoder(object):
    """Decodes the MaxMind DB data section format.

    `base` is where pointers are counted from: the start of the data
    section, or of the metadata when decoding that.
    """

    def __init__(self, buf, base):
        self.buf = buf
        self.base = base

    def _bytes(self, offset, size):
        return bytearray(self.buf[offset:offset + size])

    def _uint(self, offset, size):
        value = 0
        for b in self._bytes(offset, size):
            value = (value << 8) | b
        return value

    def decode(self, offset):
        """Return (value, offset just past it)."""
        ctrl = self._bytes(offset, 1)[0]
        offset += 1
        type_ = ctrl >> 5

        if type_ == 1:  # pointer
            ss = (ctrl >> 3) & 0x3
            vvv = ctrl & 0x7
            if ss == 0:
                ptr = (vvv << 8) | self._uint(offset, 1)
            elif ss == 1:
                ptr = ((vvv << 16) | self._uint(offset, 2)) + 2048
            elif ss == 2:
                ptr = ((vvv << 24) | self._uint(offset, 3)) + 526336
            else:
                ptr = self._uint(offset, 4)
            value, _ = self.decode(self.base + ptr)
            return value, offset + ss + 1

        if type_ == 0:  # extended type
            type_ = 7 + self._bytes(offset, 1)[0]
            offset += 1

        size = ctrl & 0x1f
        if size == 29:
            size = 29 + self._uint(offset, 1)
            offset += 1
        elif size == 30:
            size = 285 + self._uint(offset, 2)
            offset += 2
        elif size == 31:
            size = 65821 + self._uint(offset, 3)
            offset += 3

        if type_ == 2:  # utf-8 string
            return self._bytes(offset, size).decode('utf-8'), offset + size
        if type_ == 7:  # map
            result = {}
            for _ in range(size):
                key, offset = self.decode(offset)
                result[key], offset = self.decode(offset)
            return result, offset
        if type_ == 11:  # array
            result = []
            for _ in range(size):
                item, offset = self.decode(offset)
                result.append(item)
            return result, offset
        if type_ in (5, 6, 9, 10):  # unsigned ints
            return self._uint(offset, size), offset + size
        if type_ == 8:  # int32
            value = self._uint(offset, size)
            if size == 4 and value & 0x80000000:
                value -= 0x100000000
            return value, offset + size
        if type_ == 3:  # double
            return struct.unpack('!d', bytes(self._bytes(offset, 8)))[0], offset + 8
        if type_ == 15:  # float
            return struct.unpack('!f', bytes(self._bytes(offset, 4)))[0], offset + 4
        if type_ == 4:  # raw bytes
            return bytes(self._bytes(offset, size)), offset + size
        if type_ == 14:  # boolean, value is in the size field
            return size != 0, offset
        raise InvalidDatabaseError('Unsupported data type %d at %d' % (type_, offset))


class CountryByIP(object):

    def __init__(self, filename):
        fp = open(filename, 'rb')
        try:
            self._buf = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
        finally:
            fp.close()

        meta_start = self._buf.rfind(METADATA_MARKER)
        if meta_start < 0:
            raise InvalidDatabaseError('%s is not a MaxMind DB file' % filename)
        meta_start += len(METADATA_MARKER)
        self.metadata, _ = _Decoder(self._buf, meta_start).decode(meta_start)

        self.node_count = self.metadata['node_count']
        self.record_size = self.metadata['record_size']
        self.ip_version = self.metadata['ip_version']
        if self.record_size not in (24, 28, 32):
            raise InvalidDatabaseError('Unsupported record size %d' % self.record_size)
        self._node_bytes = self.record_size * 2 // 8
        tree_size = self.node_count * self._node_bytes
        self._decoder = _Decoder(self._buf, tree_size + DATA_SECTION_SEPARATOR)

        # IPv4 addresses live under ::/96 in an IPv6 tree. Find that node once.
        self._ipv4_start = 0
        if self.ip_version == 6:
            node = 0
            for _ in range(96):
                if node >= self.node_count:
                    break
                node = self._read_record(node, 0)
            self._ipv4_start = node

    def _read_record(self, node, bit):
        offset = node * self._node_bytes
        b = bytearray(self._buf[offset:offset + self._node_bytes])
        if self.record_size == 24:
            b = b[3:6] if bit else b[0:3]
            return (b[0] << 16) | (b[1] << 8) | b[2]
        if self.record_size == 28:
            if bit:
                return ((b[3] & 0x0f) << 24) | (b[4] << 16) | (b[5] << 8) | b[6]
            return ((b[3] & 0xf0) << 20) | (b[0] << 16) | (b[1] << 8) | b[2]
        b = b[4:8] if bit else b[0:4]
        return struct.unpack('!I', bytes(b))[0]

    def lookup(self, ip):
        """Return the full data record for ip, or None if it has none."""
        ip = ip.strip()
        if ip.lower().startswith('::ffff:') and '.' in ip:
            ip = ip[7:]  # IPv4-mapped IPv6 -> plain IPv4
        if ':' in ip:
            if self.ip_version != 6:
                return None
            packed = socket.inet_pton(socket.AF_INET6, ip)
            node = 0
        else:
            packed = socket.inet_aton(ip)
            if ip.count('.') != 3:
                raise ValueError('Invalid IPv4 address %r' % ip)
            node = self._ipv4_start

        bits = bytearray(packed)
        for i in range(len(bits) * 8):
            if node >= self.node_count:
                break
            node = self._read_record(node, (bits[i >> 3] >> (7 - (i & 7))) & 1)

        if node == self.node_count:
            return None
        if node < self.node_count:
            raise InvalidDatabaseError('Search tree ran out of address bits')
        offset = node - self.node_count - DATA_SECTION_SEPARATOR
        value, _ = self._decoder.decode(self._decoder.base + offset)
        return value

    def __getitem__(self, ip):
        record = self.lookup(ip)
        try:
            return str(record['country']['iso_code']).upper()
        except (TypeError, KeyError):
            raise KeyError(ip)
