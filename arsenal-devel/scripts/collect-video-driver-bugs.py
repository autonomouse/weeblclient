#!/usr/bin/python

import simplejson as json
import socket
from optparse import OptionParser
from arsenal.arsenal_lib import *
from lpltk import *

usage = '''
%prog [options] <driver-name> [release-name]
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

total_count      = 0
driver_name      = args[0]
release_name     = None
if len(args) == 2:
    release_name = args[1]
try:
    lp          = LaunchpadService(config={'read_only':True})
    d           = lp.launchpad.distributions["ubuntu"]
    records     = []
except:
    sys.exit(7)


source_pkgs = ["linux", "mesa"]
if driver_name == "radeon":
    source_pkgs.append("xserver-xorg-video-ati")
else:
    source_pkgs.append("xserver-xorg-video-%s" %(driver_name))

try:
    for source_pkg in source_pkgs:
        dbg("source:  %s\n" %(source_pkg))
        if not d:
            d           = lp.launchpad.distributions["ubuntu"]
        s = d.getSourcePackage(name = source_pkg)

        tags = ['-omit', '-kubuntu', '-xubuntu', '-ppc']
        if source_pkg in ["linux", "mesa"]:
            tags.append(driver_name)
        if release_name:
            tags.append(release_name)

        for bugtask in s.searchTasks(tags=tags, tags_combinator="All"):
            bug = ArsenalBug(bugtask.bug, lp.launchpad)
            bug.source_pkg = source_pkg

            records.append(bugtask_as_dict(bug, bugtask))

except HTTPError, e:
    if is_launchpad_down(e):
        sys.exit(7)
    else:
        sys.stderr.write("HTTPError Exception encountered: %s\n" %(bugtask.bug.id, e))
        raise
except socket.error as e:
    # Network is down.  Skip for now                                                                  
    sys.exit(7)
except:
    sys.stderr.write("Unknown exception encountered\n")
    raise

report = {
    'keys'      : [ 'id', 'title', 'importance', 'status', 'target' ],
    'bug_tasks' : records
}

print json.dumps(report, indent=4)

# TODO:  lazr.restfulclient.errors.HTTPError: HTTP Error 302: Found
