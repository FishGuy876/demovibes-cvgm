#!/usr/bin/python
# this is a custom parser for mtrace log files to help find memory leaks
#
# to obtain the log file you need to
#   1. export MALLOC_TRACE=foo.log
#   2. call mtrace() at the beginning of your program
#   3. run your program
#   4. run this script with foo.log
#
# the output has three columns.
# 1st column: number of unfreed blocks
# 2nd column: total size of blocks in bytes
# 3rd column: where the memory was originated
#
# not everything in that list might be a true memory leak. observe
# over time. you are looking for a growing number in the first column

import sys

memmap  = {}
callmap = {}

if len(sys.argv) != 2:
    print 'syntax: mtrace.py log-file'
    exit()

for line in open(sys.argv[1]):
    tok = line.split()
    if not tok or tok[0] != '@' or len(tok) < 4:
        print 'skipping "%s"' % line[:-1]
        continue
        
    call = intern(tok[1])
    mode = tok[2]
    addr = int(tok[3], 16)
    size = int(tok[-1], 16)

    if mode in ['+', '>']:
        memmap[addr] = (call, size) 
    elif mode in ['-', '<'] and addr in memmap:
        del memmap[addr]
    else:
        print 'skipping "%s"' % line[:-1]

for addr, val in memmap.iteritems():
    call, size = val
    if call in callmap:
        total, hits = callmap[call]
        callmap[call] = (total + size, hits + 1)
    else:
        callmap[call] = (size, 1)

leaklist = []
total_leak = 0
for call, val in callmap.iteritems():
    size, hits = val
    total_leak += size
    leaklist.append((hits, size, call))

for leak in sorted(leaklist):
    print '%5d %7d %s' % leak
print 'total %d bytes' % total_leak
