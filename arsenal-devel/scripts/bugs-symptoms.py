#!/usr/bin/python

import simplejson as json
import socket
from arsenal.arsenal_lib import *
from lpltk import LaunchpadService

if len(sys.argv) < 2:
    sys.stderr.write("Usage: " + sys.argv[0] + " <source-package>\n")
    exit(1)

total_count = 0
source_pkgs = sys.argv[1:]
lp          = LaunchpadService(config={'read_only':True})
d           = lp.launchpad.distributions["ubuntu"]

# TODO:  It would be interesting to parse these off https://wiki.ubuntu.com/X/Tagging
all_symptoms = [
    'error-exit',
    'no-screens',
    'crash',
    'freeze',

    'corruption',
    'tearing',
    'resolution',
    'performance',

    'dual-head',
    'backlight',
    'videoplayback',
    'ghost-monitor',
    'edid',
    '3d',
    'compiz',
    'resume',
    'cropped',

    'font-size',
    'black-screen',
    'vt-switch',
    'tv-out',
    'high-cpu',

    'mouse-pointer',
    'error-message',
    ]

regex_chipset = re.compile('^\[(\w+).*?\] *(.*)$', re.IGNORECASE)

bugs = []
try:
    series_name = None
    for series in d.series:
        if series.status == 'Current Stable Release':
            series_name = series.name
    if series_name is None:
        sys.stderr.write("Couldn't look up the current stable release name")
        sys.exit(1)

    tags = [ "-kubuntu", "-xubuntu", "-ppc", "-omit", series_name ]
    for source_pkg in source_pkgs:
        s = d.getSourcePackage(name = source_pkg)
        for bugtask in s.searchTasks(tags=tags):

            arsenal_bug = ArsenalBug(bugtask.bug, lp.launchpad)
            arsenal_bug.source_pkg = source_pkg

            symptoms = []
            for tag in bugtask.bug.tags:
                if tag in all_symptoms:
                    symptoms.append(tag)

            m = regex_chipset.match(arsenal_bug.title)
            if m:
                chip = m.group(1)
                title = m.group(2)
            else:
                chip = ''
                title = arsenal_bug.title

            bug = bugtask_as_dict(arsenal_bug, bugtask)
            bug['symptoms'] = symptoms
            bug['chip'] = chip
            bugs.append(bug)

    print json.dumps(bugs, indent=4)

except socket.error as e:
    excType, excValue, excTraceback = sys.exc_info()
    if excValue:
        sys.stderr.write("  %s\n" %(excValue))
    sys.exit(7)

except HTTPError as e:
    if e.response["status"] == "503":
        sys.exit(7)
    if e.response["status"] == "502":
        sys.exit(7)
    if e.response["status"] == "500":
        sys.exit(7)
    if e.response["status"] == "401":
        # Could be a Launchpad OOPS.  If so, terminate.
        sys.stderr.write("Aha!  Found a 401 error.  Maybe I need to re-authenticate?")
        sys.exit(1)
    else:
        sys.stderr.write("HTTPError exception hit\n")
        sys.stderr.write("%s\n" %(e.response))
        sys.exit(1)

except:
    sys.stderr.write("Unknown exception hit\n")
    raise
