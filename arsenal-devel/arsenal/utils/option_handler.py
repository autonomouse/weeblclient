#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Command line options'''

import os.path
from optparse import OptionParser

class OptionHandler(OptionParser):
    '''Subclass of OptionParser that also tracks descriptions'''
    def __init__(self, info, app_name=None, arg_names=''):
        '''Creates an OptionParser instance for the options in this module'''
        prog = info.PROGNAME
        usage = None
        if app_name:
            self.app_name = os.path.basename(app_name)
            prog = "%s %s" %(self.app_name, info.PROGNAME)
            usage = "%s %s" %(self.app_name, arg_names)
        else:
            self.app_name = info.PROGNAME
        version = info.VERSION or "(UNRELEASED)"
        OptionParser.__init__(
            self,
            usage=usage,
            version="%s %s" %(prog, version),
            epilog="%s - %s" %(info.PROGNAME, info.SHORT_DESCRIPTION)
            )
        self.descriptions = []

    def add(self, short_opt, long_opt, **kwargs):
        '''Adds an option.

        Example:

        opt_hand.add('-d', '--debug', \
                 help='Enable debug output', \
                 action='store_true', default=False, dest='debug', \
                 desc="Turns on verbose debugging output")
        '''
        item = {
            'opts': [short_opt, long_opt],
            'text': kwargs.get('desc', ''),
            }
        self.descriptions.append(item)
        del kwargs['desc']
        self.add_option(short_opt, long_opt, **kwargs)
