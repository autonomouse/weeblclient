#!/usr/bin/python
#
# Author: Brian Murray <brian@canonical.com>
#
# List the packages for which a team is the bug subscriber
#   additionally display whether or not the package has bug reporting
#   guidelines or an acknowledgement

from __future__ import print_function

import sys
from optparse import OptionParser

from lpltk import LaunchpadService
from lpltk.LaunchpadService import LaunchpadServiceError

usage = '''
%prog [options]
'''
parser = OptionParser(usage=usage)
parser.add_option(
    '-d', '--debug',
    action='store_true', dest='DEBUG', default=False,
    help='Enable debugging output')
parser.add_option(
    '-t', '--team',
    help="Team name to find subbed packages")
parser.add_option(
    '-v', '--verbose',
    action="store_true", default=False,
    help="Show if there is bug reporting info in LP")
parser.add_option(
    '-c', '--csv',
    action="store_true", default=False,
    help="Format output for the package to team mapping csv file")
(opt, args) = parser.parse_args()

try:
    lp = LaunchpadService(config={'read_only': False})
except LaunchpadServiceError:
    sys.stderr.write("Error: Could not connect to Launchpad\n")
    sys.exit(1)

team_name = opt.team
if not team_name:
    parser.print_help()
    sys.exit(1)

team = lp.launchpad.people[team_name]

sub_pkgs = team.getBugSubscriberPackages()

if opt.verbose:
    print('source package, guidelines, acknowledgement')
    for sub_pkg in sub_pkgs:
        guidelines = 'no'
        ack = 'no'
        if sub_pkg.bug_reporting_guidelines is not None:
            guidelines = 'yes'
        if sub_pkg.bug_reported_acknowledgement is not None:
            ack = 'yes'
        print( '%s, %s, %s' % (sub_pkg.display_name.split(' ')[0], guidelines,
            ack))
else:
    for sub_pkg in sub_pkgs:
        pkg = sub_pkg.display_name.split(' ')[0]
        if opt.csv:
            print('%s,%s' % (pkg, team_name))
        else:
            print('%s' % pkg)
