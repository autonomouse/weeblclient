#!/usr/bin/env python

from sys import stderr
from text import o2str

## TODO: Use o2str, consider replacing it in ../utils

DEBUGGING = False

def dbg(*msg):
    if DEBUGGING:
        msg = ' '.join(map(str, msg))
        stderr.write("%s\n" %(msg))
        stderr.flush()

def warn(*msg):
    msg = ' '.join(map(str, msg))
    stderr.write("Warning: %s\n" %(msg))
    stderr.flush()

def ERR(*msg):
    msg = ' '.join(map(str, msg))
    stderr.write("ERROR: %s\n" %(msg))
    stderr.flush()

def die(msg, code=1):
    import sys
    ERR(msg)
    sys.exit(code)
