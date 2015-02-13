#!/usr/bin/python

# The purpose of this script is to report status of upstreamed bugs,
# principly for use in working with Intel on issues that are important
# to Ubuntu.
#
# A secondary purpose of this script (which may be worth breaking out
# separately) is to identify work-tasks relating to upstream[able] bugs.

from arsenal.arsenal_lib import *
from lpltk import LaunchpadService
import string

source_pkg  = "xserver-xorg-video-intel"
lp          = LaunchpadService(config={'read_only':True})
d           = lp.launchpad.distributions["ubuntu"]

new = 0
incomplete = 0
confirmed = 0
triaged = 0
upstreamed = 0
needs_upstreamed = 0
other = 0
fixed_upstream = 0
open_upstream = 0

tags = [d.current_series.name, '-kubuntu', '-xubuntu', '-ppc', '-omit']

print "---- Ubuntu ----   ------ FDO ------"
print "%-7s %-9s  %-6s %-9s  %s" % ("LP#", "Priority", "FDO#", "Status", "Description")

s = d.getSourcePackage(name = source_pkg)
for bugtask in s.searchTasks(tags = tags, tags_combinator = "All"):
    bug = ArsenalBug(bugtask.bug, lp.launchpad)
    title = bug.title

    best_watch = None
    for task in bugtask.bug.bug_tasks:
        if not task.bug_watch:
            continue
        if task.bug_watch.bug_tracker.name != "freedesktop-bugs":
            continue
        best_watch = task.bug_watch

        if task.bug_watch.remote_status == "RESOLVED FIXED" \
                or task.bug_watch.remote_status == "RESOLVED DUPLICATE":
            fixed_upstream += 1
        elif task.bug_watch.remote_status != None:
            open_upstream += 1
    if not best_watch or not best_watch.remote_status:
        continue

    upstream_bug = best_watch.remote_bug
    upstream_status = best_watch.remote_status.split(' ').pop()
    if upstream_status == "FIXED":
        continue

    # LP: 389269 - launchpad is not providing remote_importance on bugs
    print "%-7s %-9s  %-6s %-9s  %s" % (bug.id, bugtask.importance, upstream_bug,
                                        upstream_status, title)
    if bugtask.status == "New":
        new += 1
    elif bugtask.status == "Incomplete":
        incomplete += 1
    elif bugtask.status == "Confirmed":
        confirmed += 1
    elif bugtask.status == "Triaged":
        triaged += 1
        if not upstream_bug:
            needs_upstreamed += 1
    else:
        other += 1

print
print "%2d bugs are unprocessed" % (new)
print "%2d bugs are waiting on reporters for more information" % (incomplete)
print "%2d bugs are pending Ubuntu review" % (confirmed)
print "%2d bugs need upstreamed" % (needs_upstreamed)
print "%2d bugs are in process by Ubuntu" % (other)
print
print "%2d bugs are fixed upstream" % (fixed_upstream)
print "%2d bugs are waiting on upstream" % (open_upstream)

