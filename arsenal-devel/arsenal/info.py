#!/usr/bin/env python
# -*- coding: utf-8 -*-

from info_utils import (
    _contributor,
    _get_version_from_debian_changelog
    )

'''High level package information'''
PROGNAME = 'arsenal'
URL = ''
EMAIL = ''
VERSION = _get_version_from_debian_changelog()
DATE_STARTED = '2008-09-26'
DATE_COPYRIGHT = '2008'
LICENSE_URL = 'http://www.gnu.org/copyleft/gpl.html'

SHORT_DESCRIPTION = 'Report generation tools for Launchpad bug reports'

DESCRIPTION = """
Arsenal generates custom listings of bug reports suited to project
managers and defect analysts.
"""

LEAD_DEVELOPER = _contributor(
    'Bryce Harrington', 'bryce@canonical.com', started='2008-09-26',
    roles=['lead', 'developer'], translating=None,
    )

CONTRIBUTORS = [
    _contributor('Andy Whitcroft', 'apw@canonical.com', roles='developer'),
    _contributor('Brian Murray', 'brian@canonical.com', roles='developer'),
    _contributor('Brad Figg', 'brad.figg@canonical.com', roles='developer'),
    _contributor('Chris J Arges', 'chris.j.arges@canonical.com', roles='developer'),
    _contributor('Joseph Salisbury', 'joseph.salisbury@canonical.com', roles='developer'),
    _contributor('Jeremy Foshee', 'jeremy.foshee@canonical.com', roles='developer'),
    _contributor('Kamran Riaz Khan', 'krkhan@inspirated.com', roles='developer'),
    _contributor('Kees Cook', 'kees@outflux.net', roles='developer'),
    _contributor('Leann Ogasawara', 'ogasawara@canonical.com', roles='developer'),
    _contributor('Pedro Villavicencio', 'pedro@ubuntu.com', roles='developer'),
    _contributor('Robert Hooker', 'sarvatt@ubuntu.com', roles='developer'),
    ]


if __name__ == "__main__":
    print(PROGNAME, VERSION, URL)
    print("Copyright (C) %s %s <%s>" % (
        DATE_COPYRIGHT, LEAD_DEVELOPER.name, LEAD_DEVELOPER.email))
    print("\n")
    for contributor in CONTRIBUTORS:
        print("%s %s %s" % (
            contributor.name,
            contributor.display_email,
            contributor.display_roles))
