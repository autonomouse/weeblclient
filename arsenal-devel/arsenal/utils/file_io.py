#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import exists

class FileDoesntExist(BaseException):
    def __init__(self, file_name=None):
        self.file_name = file_name
    def __str__(self):
        return "The file (%s) does not exist" %(self.file_name)

def load_file(filename):
    assert(filename)
    if not exists(filename):
        raise FileDoesntExist(filename)
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines

# vi:set ts=4 sw=4 expandtab:
