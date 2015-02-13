#!/usr/bin/python
#
# display all the bug reports about a package targetted to a release

import simplejson as json
from optparse import OptionParser

from arsenal.arsenal_lib import *
from lpltk import *

usage = '''
%prog [options] <release> <source-package> [source-package ...]
'''
parser = OptionParser(usage=usage)
parser.add_option(
    '-d', '--debug',
    action='store_true', dest='DEBUG', default=False,
    help='Enable debugging output')
(options, args) = parser.parse_args()

if len(args) < 2:
    parser.print_help()
    sys.exit(1)

total_count = 0
release     = args[0]
source_pkgs = args[1:]
try:
    lp          = LaunchpadService(config={'read_only':True})
    d           = lp.launchpad.distributions["ubuntu"]
    series      = lp.load_distro_series("ubuntu", "%s" % release)
    records     = []
except:
    sys.exit(7)


try:
    for source_pkg in source_pkgs:
        dbg("source:  %s\n" %(source_pkg))
        if not d:
            d           = lp.launchpad.distributions["ubuntu"]
        s = series.getSourcePackage(name = source_pkg)
        for bugtask in s.searchTasks(omit_targeted=False):
            bug = ArsenalBug(bugtask.bug, lp.launchpad)

            records.append(bugtask_as_dict(bug, bugtask))
except:
    # If launchpad threw an exception, it's probably just LP being down.
    # We'll catch up next time we run
    sys.stderr.write("Error:  Unknown launchpad failure\n")
    sys.exit(1)


report = {
    'keys'      : [ 'id', 'title', 'importance', 'status' ],
    'bug_tasks' : records
}

print json.dumps(report, indent=4)

# TODO:  lazr.restfulclient.errors.HTTPError: HTTP Error 302: Found
