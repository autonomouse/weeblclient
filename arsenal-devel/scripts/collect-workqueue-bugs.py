#!/usr/bin/python

import simplejson as json
import socket
from optparse import OptionParser
from arsenal.arsenal_lib import *
from lpltk import *
from httplib2 import ServerNotFoundError

usage = '''
%prog [options] <release-name> [source-package ...]
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

try:
    lp          = LaunchpadService(config={'read_only':True})
    d           = lp.launchpad.distributions["ubuntu"]
    records     = []
except:
    sys.exit(7)

devel_name = d.current_series.name
release_name = args[0]
source_pkgs = args[1:]
try:
    for source_pkg in source_pkgs:
        dbg("source:  %s\n" %(source_pkg))
        if not d:
            d           = lp.launchpad.distributions["ubuntu"]
        s = d.getSourcePackage(name = source_pkg)
        bug_tracker_url = None
        up = s.upstream_product
        if (up is not None and up.bug_tracker is not None):
            bug_tracker_url = up.bug_tracker.base_url

        tags = [release_name, '-omit', '-kubuntu', '-xubuntu', '-ppc']
        if release_name != devel_name:
            tags.append('-%s' %(devel_name))
        for bugtask in s.searchTasks(tags=tags, tags_combinator="All", status=[
            'New', 'Incomplete (with response)', 'Confirmed', 'Triaged', 'In Progress']):

            # Exclude bugs that have open upstream bugzilla tasks
            open_upstream = False
            complete_upstream = False
            for sibling_task in bugtask.related_tasks:
                if sibling_task.bug_watch is None:
                    continue
                bt = sibling_task.bug_watch.bug_tracker
                if bt is not None:
                    if bt.base_url == bug_tracker_url:
                        if sibling_task.is_complete:
                            complete_upstream = True
                        else:
                            open_upstream = True
                            break
            if open_upstream:
                continue

            bug = ArsenalBug(bugtask.bug, lp.launchpad)
            bug.source_pkg = source_pkg

            try:
                bug_dict = bugtask_as_dict(bug, bugtask)
                bug_dict['complete_upstream'] = complete_upstream
                for tag in ['ubuntu', release_name, 'i386', 'amd64',
                            'running-unity', 'compiz-0.9',
                            'apport-bug', 'apport-crash', 'apport-collect', 'apport-collected', 'apport-package']:
                    if tag in bug_dict['tags']:
                        bug_dict['tags'].remove(tag)
                records.append(bug_dict)
            except:
                pass

except HTTPError, e:
    if is_launchpad_down(e):
        sys.exit(7)
    else:
        sys.stderr.write("HTTPError Exception encountered: %s %s\n" %(bugtask.bug.id, e))
        raise
except socket.error as e:
    # Network is down.  Skip for now
    sys.exit(7)
except ServerNotFoundError as e:
    if is_launchpad_down(e):
        sys.exit(7)
    else:
        sys.stderr.write("ServerNotFoundError: %s %s\n" %(bugtask.bug.id, e))
        raise
except:
    sys.stderr.write("Unknown exception encountered\n")
    raise

report = {
    'keys'      : [ 'id', 'title', 'importance', 'status', 'target' ],
    'bug_tasks' : records
}

print json.dumps(report, indent=4)

# TODO:  lazr.restfulclient.errors.HTTPError: HTTP Error 302: Found
