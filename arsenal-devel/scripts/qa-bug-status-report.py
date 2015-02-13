#!/usr/bin/python
#
# make a neato report tracking bug tasks, assignments and
# days for a release
#
# example output:
#
# Lucid Quality (wrt Bugs) Status Report
# 34 days left and 309 bug tasks to fix
# Barring no new work we need to fix 9 bug tasks a day now
# The Canonical Desktop Team needs to deal with 19 bug tasks
# Chris Coulson is the most overtasked with 10 bug tasks
# Martin Pitt is rockin' with 69 bug tasks fixed
# Yesterday's hero was Martin Pitt with 2 bug tasks fixed

import datetime
import re
import json
from optparse import OptionParser

from arsenal.arsenal_lib import *
from lpltk import *
from operator import itemgetter
from calendar import day_name

usage = '''
%prog [options]
'''
parser = OptionParser(usage=usage)
parser.add_option(
    '-d', '--debug',
    action='store_true', dest='DEBUG', default=False,
    help='Enable debugging output')
(options, args) = parser.parse_args()

if len(args) < 0:
    parser.print_help()
    sys.exit(1)

try:
    lp           = LaunchpadService(config={'read_only':True})
    d            = lp.launchpad.distributions["ubuntu"]
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

def count_work(bug_tasks, yesterday):
    counts = { 'people': {}, 'teams': {}, 'yesterday': {} }
    for task in bug_tasks:
        key = 'people'
        if task.assignee:
            if task.assignee.is_team:
               key = 'teams'
            assignee = task.assignee.display_name
            if yesterday and fix_date_type(task.date_fix_released) == yesterday:
                day_key = 'yesterday'
                counts[day_key]['%s' % assignee] = counts[day_key].setdefault(assignee, 0) + 1
            counts[key]['%s' % assignee] = counts[key].setdefault(assignee, 0) + 1
        if not task.assignee:
            if yesterday and fix_date_type(task.date_fix_released) == yesterday:
                day_key = 'yesterday'
                for message in task.bug.messages:
                    if message.owner.name == 'janitor':
                        author_re = re.compile(r'^\s*--\s*([^<]+)\s*<.*$') 
                        last_line = message.content.split("\n")[-1]
                        try:
                            fixer = author_re.search(last_line).group(1).strip()
                        except AttributeError:
                            print last_line
                        # to use[ Brian Murray ] you need to check for the [ ] block
                        # and see if the task.bug.id is appears before the [ ] block
                        # thoughts
                        # for line in message.content.splits("\n")
                        #   if props.search(line)
                        #       if task.bug.id in some regex search:
                        #       r'.*LP: #(\d+[^,\)]+)' (remaining changes?)
                        #           fixer = props.search(line).group(1).strip()
                        #           break
                        #   else:
                        #       last_line stuff
                        counts[day_key]['%s' % fixer] = counts[day_key].setdefault(fixer, 0) + 1
    hi_person, hi_person_count = sorted(counts['people'].items(), key=itemgetter(1), reverse=True)[0]
    hi_team, hi_team_count = sorted(counts['teams'].items(), key=itemgetter(1), reverse=True)[0]
    if counts['yesterday']:
        y_hi_person, y_hi_person_count = sorted(counts['yesterday'].items(), key=itemgetter(1), reverse=True)[0]
    else:
        y_hi_person = 'nobody'
        y_hi_person_count = 0

    return hi_person, hi_person_count, hi_team, hi_team_count, y_hi_person, y_hi_person_count 

def find_date_targeted(release):
    # Why does LP have the time if it is always 00:00? LP: #326384
    latest = datetime.datetime.today().date()
    for active_milestone in release.active_milestones:
        if active_milestone.date_targeted and fix_date_type(active_milestone.date_targeted) > latest:
            latest = fix_date_type(active_milestone.date_targeted)
    return latest

def find_open_bug_tasks(release):
    quantity = ''
    counts = { 'people': {}, 'teams': {} }

    bug_tasks = release.searchTasks(omit_targeted=False)
    quantity = int(bug_tasks._wadl_resource.representation['total_size'])
    # maybe we should count only the bug tasks for the next milestone instead of everything?
    # regardless we won't include the tasks milestoned for lucid-updates - using -updates should
    #   be robust enough
    for milestone in release.active_milestones:
        if milestone.name == "%s-updates" % release.name:
            updates_milestone = milestone
    #updates_milestone = lp.load("%s/ubuntu/+milestone/%s-updates" % ( lp._root_uri, release.name ) )
    updates_tasks = release.searchTasks(omit_targeted=False,milestone=updates_milestone)
    updates_count = int(updates_tasks._wadl_resource.representation['total_size'])
    quantity = quantity - updates_count

    poorsap, person_count, poorteam, team_count, nothing, ignored = count_work(bug_tasks, None)
    return quantity, poorsap, person_count, poorteam, team_count 

def find_fixed_bug_tasks(release, yesterday):
    bug_tasks = release.searchTasks(omit_targeted=False,
                                    status=['Fix Released'],
                                    modified_since=yesterday)
    rockstar, rockstar_count, team, team_count, yesterday_rockstar, yesterday_rockstar_count  = count_work(bug_tasks, yesterday)
    return rockstar, rockstar_count, yesterday_rockstar, yesterday_rockstar_count

# 2010-04-03 - why isn't this working?
#def find_count_of_bugs(**args):
    #bug_tasks = release.searchTasks(omit_targeted=False,status=['%s'],tags=['%s'] % (status, tag))
    #bug_tasks = release.searchTasks(omit_targeted=False,status=['%s' % status],tags=['%s' % tag])
#    bug_tasks = release.searchTasks(**args)
#    quantity = int(bug_tasks._wadl_resource.representation['total_size'])

now = datetime.date.today()
yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
yesterday = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
expected = find_date_targeted(release)
#expected = datetime.date(2010, 04, 15)
time_to_release = abs(expected - now)

# 2010-04-03 looking for count of each status and open count for specific tags
status_count = {}
for status in ['New', 'Incomplete', 'Confirmed', 'Triaged', 'In Progress', \
               'Fix Committed', 'Fix Released', 'Invalid', "Won't Fix" ]:
    args = { 'status': status, 'tags': [], 'omit_targeted': False }
    bug_tasks = release.searchTasks(**args)
    status_count[status] = int(bug_tasks._wadl_resource.representation['total_size'])
    #status_count[status] = find_count_of_bugs(**args)

importance_count = {}
critical_bugs = {}
for importance in ['Undecided', 'Wishlist', 'Low', 'Medium', 'High', 'Critical']:
    open_stati = ['New', 'Incomplete', 'Confirmed', 'Triaged', 'In Progress', 'Fix Committed']
    args = { 'status': open_stati, 'importance': importance, 'tags': [], 'omit_targeted': False }
    bug_tasks = release.searchTasks(**args)
    importance_count[importance] = int(bug_tasks._wadl_resource.representation['total_size'])
    if importance == 'Critical':
        for task in bug_tasks:
            critical_bugs[task.bug.id] = task.bug.title

tag_count = {}
regression_bugs = {}
for tag in ['regression-potential']:
    open_stati = ['New', 'Incomplete', 'Confirmed', 'Triaged', 'In Progress', 'Fix Committed']
    args = { 'status': open_stati, 'tags': tag, 'omit_targeted': False }
    bug_tasks = release.searchTasks(**args)
    tag_count[tag] = int(bug_tasks._wadl_resource.representation['total_size'])
    for task in bug_tasks:
        regression_bugs[task.bug.id] = task.bug.title

quantity, poorsap, person_count, poorteam, team_count = find_open_bug_tasks(release)
rockstar, rockstar_count, yesterday_rockstar, yesterday_rockstar_count = find_fixed_bug_tasks(release, yesterday)

# instead of a print write this to a file
# then write regression related ones to a different file
print "%s %s Quality Bug Status Report" % ( release.distribution.name.title(), release.version )
print ""

print "Hello Ubuntu Developers,"
print ""
print "%s days left and %s bug tasks to fix. [1]" % (time_to_release.days, quantity)
print "Barring no new work, we need to fix %i bug tasks per day now." %  ( round(float(quantity)/float(time_to_release.days)) )
print ""

print "The focus of bug fixing should be on the following tasks:"
print ""

print "1. The %d Critical bug tasks. [2]" % importance_count['Critical']
print ""
for bug in critical_bugs.keys():
    print "%s" % ( critical_bugs[bug] )
    print " http://launchpad.net/bugs/%i" % bug
print ""

print "2. The %d bug tasks that might cause a regression in %s. [3]" % ( tag_count['regression-potential'], release.displayname )
print "3. The %d High bug tasks. [4]" % importance_count['High']
print ""

print "The %s needs to deal with %i bug tasks." % ( poorteam, team_count )
print "%s is the most overtasked with %i bug tasks." % ( poorsap, person_count )
print "%s is rockin' with %i bug tasks fixed!" % ( rockstar, rockstar_count )
if yesterday_rockstar != 'nobody':
    print "%s's hero was %s with %i bug tasks fixed!" % ( day_name[yesterday.weekday()], yesterday_rockstar, yesterday_rockstar_count )
else:
    print "%s did not have a hero - it could have been you!" % ( day_name[yesterday.weekday()] )
print ""

print "Thank you for your focus on quality."
print ""
print "Regards,"
print ""
print "Marjo"
print ""
print "[1] https://bugs.launchpad.net/ubuntu/%s/+bugs" % ( release.name )
print "[2] https://bugs.launchpad.net/ubuntu/%s/+bugs?search=Search&field.importance=Critical" % ( release.name )
print "[3] https://bugs.launchpad.net/ubuntu/%s/+bugs?field.tag=regression-potential" % ( release.name )
print "[4] https://bugs.launchpad.net/ubuntu/%s/+bugs?search=Search&field.importance=High" % ( release.name )


#print "[1] regression-potential tagged bug reports"
#for bug in regression_bugs.keys():
#    print "%s" % ( regression_bugs[bug] )
#    print " http://launchpad.net/bugs/%i" % bug
