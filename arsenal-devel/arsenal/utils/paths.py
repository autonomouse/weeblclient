#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import (
    relpath,
    dirname,
    expanduser,
    exists,
    join
    )

def find_datadir(program):
    for d in [
        relpath(join(dirname(__file__), "../../data")),
        expanduser("~/.local/share/%s" %(program)),
        "/usr/local/share/%s" %(program),
        "/usr/share/%s" %(program)]:
        if exists(d):
            return d
    return None


if __name__ == "__main__":
    print find_datadir('arsenal')

# vi:set ts=4 sw=4 expandtab:
