#!/usr/bin/python
#
# display all the ubuntu bug reports with a specific tag
#
# 2010-03-18 - maybe ls-tag-json should be smarter and not require
# source-packages instead of having two scripts

import simplejson as json
from optparse import OptionParser

from arsenal.arsenal_lib import *
from lpltk import *
import sys

usage = '''
%prog [options] <tag>
'''
parser = OptionParser(usage=usage)
parser.add_option(
    '-d', '--debug',
    action='store_true', dest='DEBUG', default=False,
    help='Enable debugging output')
(options, args) = parser.parse_args()

if len(args) < 1:
    parser.print_help()
    sys.exit(1)

total_count     = 0
tag             = args[0]

try:
    lp          = LaunchpadService(config={'read_only':True})
    project     = lp.launchpad.distributions["ubuntu"]
    records     = []
except:
    sys.exit(7)

try:
    if not project:
        project = lp.launchpad.distributions["ubuntu"]
    for bugtask in project.searchTasks(tags=tag):
        bug = ArsenalBug(bugtask.bug, lp.launchpad)
        records.append(bugtask_as_dict(bug, bugtask))
except:
    # If launchpad threw an exception, it's probably just LP being down.
    # We'll catch up next time we run
    sys.stderr.write("Error:  Unknown launchpad failure\n")
    sys.exit(1)


report = {
    'keys'      : [ 'id', 'title', 'target', 'importance', 'status', 'heat' ],
    'bug_tasks' : records
}

print json.dumps(report, indent=4)

# TODO:  lazr.restfulclient.errors.HTTPError: HTTP Error 302: Found
