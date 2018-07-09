#!/usr/bin/env python
__version__ = '0.5'

import re, struct


is_IP = re.compile('^%s$' % r'\.'.join([r'(?:(?:2[0-4]|1\d|[1-9])?\d|25[0-5])']*4)).match


class CountryByIP:

    def __init__(self, filename):
        self.fp = open(filename, 'rb')

    def __getitem__(self, ip):
        offset = 0
        fp = self.fp
        for part in ip.split('.'):
            start = offset+int(part)*4
            fp.seek(start)
            value = fp.read(4)
            assert len(value)==4
            if value[:2]=='\xFF\xFF':
                if value[2:]=='\x00\x00':
                    raise KeyError(ip)
                else:
                    return value[2:]
            offset = struct.unpack('!I', value)[0]
        raise RuntimeError('ip2cc database is broken') # must never reach here

import iso3166_1

# Additional codes used by registrars
cc2name = iso3166_1.cc2name.copy()
cc2name.update({
    #'UK': cc2name['GB'],
    #'YU': 'FORMER YUGOSLAVIA',
    'CS': 'SERBIA AND MONTENEGRO',
    'EU': 'EUROPEAN UNION',
    'AP': 'ASSIGNED PORTABLE',
})


if __name__=='__main__':
    import sys, os
    db_file = os.path.splitext(sys.argv[0])[0]+'.db'
    if os.environ.get('REQUEST_URI'):
        import cgi
        form = cgi.FieldStorage()
        try:
            addr = form['addr'].value
        except (KeyError, AttributeError):
            addr = ''
        msg = ''

        if addr:
            if not is_IP(addr):
                msg = '%s is not valid IP address' % cgi.escape(addr)
            else:
                db = CountryByIP(db_file)
                try:
                    cc = db[addr]
                except KeyError:
                    msg = 'Information for %s not found' % cgi.escape(addr)
                else:
                    msg = '%s is located in %s' % (cgi.escape(addr),
                                                   cc2name.get(cc, cc))
        script_name = os.environ['SCRIPT_NAME']
        print '''\
Content-Type: text/html

<html>
<head><title>Country By IP</title></head>
<body>
<h1>Country By IP</h1>
<form action="%(script_name)s">
<input type="text" name="addr" value="%(addr)s">
</form>
%(msg)s
<hr>
<a href="http://ppa.sf.net/#ip2cc">ip2cc %(__version__)s</a>
</body>
</html>''' % vars()

    elif len(sys.argv)==2:
        addr = sys.argv[1]
        if is_IP(addr):
            ip = addr_str = addr
        else:
            from socket import gethostbyname, gaierror
            try:
                ip = gethostbyname(addr)
            except gaierror, exc:
                sys.exit(exc)
            else:
                addr_str = '%s (%s)' % (addr, ip)
        try:
            db = CountryByIP(db_file)
        except IOError, exc:
            import errno
            if exc.errno==errno.ENOENT:
                sys.exit('Database not found. Run update.py to create it.')
            else:
                sys.exit('Cannot open database: %s' % exc)
        try:
            cc = db[ip]
        except KeyError:
            sys.exit('Information for %s not found' % addr)
        else:
            print '%s is located in %s' % (addr_str, cc2name.get(cc, cc))
    else:
        sys.exit('Usage:\n\t%s <address>' % sys.argv[0])
