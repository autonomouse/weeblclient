#!/usr/bin/python

# Find the quantity of bugs opened and resolved for a release on a daily basis
# and output the data as a csv file for use with gnuplot.  The release defaults 
# to the current series or can be a command line argument.

# Example Output:
# Date, Cycle Day, Day Opened, Day Resolved, Total Opened, Total Resolved, Total Total
# 2009-10-29, 0, 1, 1, 0, 1, 1
# 2009-10-30, 1, 16, 0, 16, 1, 17

import sys
import datetime
from optparse import OptionParser

from arsenal.arsenal_lib import *
from lpltk import *

usage = '''
%prog [options] [old-release]
'''
parser = OptionParser(usage=usage)
parser.add_option(
    '-d', '--debug',
    action='store_true', dest='DEBUG', default=False,
    help='Enable debugging output')
(options, args) = parser.parse_args()

if len(args) < 1:
    old_release = ''
else:
    old_release = args[0]

try:
    lp          = LaunchpadService(config={'read_only':True})
    d           = lp.launchpad.distributions["ubuntu"]
    if old_release:
        release      = lp.load_distro_series("ubuntu", "%s" % old_release)
        release_name = release.name
    else:
        release      = d.current_series
        release_name = d.current_series.name
except ValueError:
    sys.exit(7)

def fix_date_type(date_object):
    # on Hardy launchpadlib dates are strings not datetimes
    try:
        date = datetime.datetime.strptime(date_object[:10], "%Y-%m-%d").date()
    except TypeError:
        date = date_object.date()
    return date

opened = {} # opening dates and counts { date: count, date: count }
resolved = {} # closed dates and counts { date: count, date: count }

tasks = release.searchTasks(status=['New','Incomplete','Confirmed','Triaged',\
                            'In Progress','Fix Committed', 'Fix Released',\
                            "Won't Fix",'Invalid'],omit_targeted=False)

for task in tasks:
    #print "LP: #%d" % task.bug.id
    # Am I going to regret not having the extra granularity?
    if task.status == 'Fix Released':
        try:
            date = fix_date_type(task.date_fix_released)
        except AttributeError:
            date = fix_date_type(task.date_closed)
        #print "LP: #%d, %s" % ( task.bug.id, task.status )
        resolved[date] = resolved.setdefault(date, 0) + 1
    elif task.status in [ 'Invalid', "Won't Fix" ]:
        #print "LP: #%d, %s" % ( task.bug.id, task.status )
        date = fix_date_type(task.date_closed)
        resolved[date] = resolved.setdefault(date, 0) + 1
    date = fix_date_type(task.date_created)
    opened[date] = opened.setdefault(date, 0) + 1

# check every date to see if it exists in the dictionary because we'd want 0's too
start_date = release.date_created.date()
today = datetime.datetime.today().date()
day_count = today - start_date
count = datetime.timedelta(days=0)
total_open = total_resolved = current_open = 0

print "Date, Cycle Day, Day Opened, Day Resolved, Total Opened, Total Resolved, Total Total"
while count <=  day_count:
    current = start_date + count
    try:
        opened_count = opened[current]
    except KeyError:
        opened_count = 0
    total_open += opened_count
    try:
        resolved_count = resolved[current]
    except KeyError:
        resolved_count = 0
    total_resolved += resolved_count
    current_open = ( total_open - total_resolved )
    print "%s, %d, %d, %d, %d, %d, %d" % ( current, count.days, opened_count, resolved_count, current_open, total_resolved, total_open )
    count += datetime.timedelta(days=1)
