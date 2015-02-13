#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

class _contributor:
    '''Information about a person contributing to this project'''
    def __init__(self, name, email, started=None, roles=None, translating=None):
        self.name = name
        self.email = email
        self.started = started
        if roles is None:
            self.roles = []
        elif type(roles) is not list:
            self.roles = [roles]
        else:
            self.roles = roles
        self.translation_languages = translating
        return

    def to_dict(self):
        '''Returns the object in a dict suitable for json'''
        return self.__dict__

    @property
    def display_email(self):
        '''Formatted string version of email address'''
        if self.email:
            return '<%s>' % self.email
        else:
            return ''

    @property
    def display_roles(self):
        '''Formatted string version of roles list'''
        if self.roles:
            return '[%s]' % ','.join(self.roles)
        else:
            return ''

# look/set what version we have
def _get_version_from_debian_changelog():
    changelog = "debian/changelog"
    if os.path.exists(changelog):
        head = open(changelog).readline()
        match = re.compile(".*\((.*)\).*").match(head)
        if match:
            return match.group(1)

