#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# 2008-10-24
# This script finds all the members of a team and then search for Ubuntu bug
# tasks assigned to them

from launchpadlib.launchpad import Launchpad
from launchpadlib.errors import HTTPError
from launchpadlib.credentials import Credentials
from operator import itemgetter
from cgi import escape
import datetime
from datetime import datetime, date
import sys
import os
import shutil
import re

cachedir = os.path.expanduser("/home/pedro/.launchpadlib/cache/")
root = 'production'

if not os.path.exists(cachedir):
    os.makedirs(cachedir, 0700)

root = 'production'
version = "1.0"
script_name = sys.argv[0].split("/")[-1].split('.')[0]

credfile = os.path.expanduser('/home/pedro/.launchpadlib/%s.cred' % script_name)
launchpad = Launchpad.login_with(script_name, service_root=root, launchpadlib_dir=cachedir, credentials_file=credfile, version=version)

team_name = sys.argv[1]

def has_target(bug, series):
    series_url = str(series)
    for task in bug.bug_tasks:
        if str(task.self_link).startswith(series_url):
            return True
    return False

# write to this file
datafile = open('%s-assigned-bug-tasks.html' % team_name, 'w')

# this could be modified to find any project's bugs assigned to a team
ubuntu = launchpad.distributions['ubuntu']

try:
    team = launchpad.people[team_name]
except:
    print "Unknown team!"

team_members = team.participants

# creating a list of all the task collections for each team member
task_collections= []

supported_releases = ['Dapper', 'Hardy', 'Karmic', 'Lucid', 'Maverick',
                      'Natty']

counts = {}

importances = {'Critical': 1, 'High': 2, 'Medium': 3,
               'Low': 4, 'Wishlist': 5, 'Undecided': 6}

statuses = {"Won't Fix": 1, 'New': 2, 'Incomplete': 3, 'Confirmed': 4,
            'Triaged': 5, 'In Progress': 6, 'Fix Committed': 7,
            'Fix Released': 8}

# also grab the bugs assigned to the team
task_collections.append(ubuntu.searchTasks(assignee=team))

for team_member in team_members:
    # this uses the default search and only finds open bugs
    task_collections.append(ubuntu.searchTasks(assignee=team_member))

templatefile = open('/home/pedro/scripts/template.html', 'r')

for line in templatefile:
    if line.strip() == "<!-- *** Title Space *** -->":
        datafile.write("Bugs assigned to members of the %s team\n" % team_name)
    elif line.strip() == "<!-- *** Header Space *** -->":
        datafile.write("Bugs assigned to members of the %s team\n" % team_name)
    elif line.strip() == "<!-- *** Title *** -->":
          datafile.write("Bugs assigned to the canonical-desktop-team")
    elif line.strip() == "<!-- *** Table Header Space *** -->":
        table_header = "<th> </th><th>Bug Number</th>"  # bug number in this column
        table_header += "<th colspan=\"2\">Summary</th>"
        table_header += "<th>In</th>"
        table_header += "<th>Importance</th>"
        table_header += "<th>Statlus</th>"
        table_header += "<th>Release</th>"
        table_header += "<th>Milestone</th>"
        table_header += "<th>Assignee</th>"
        table_header += "<th>Date Assigned</th>"
        table_header += "<th>Regression</th>"
        table_header += "\n"
        datafile.write(table_header)
    elif line.strip() == "<!-- *** Table Body Space *** -->":
        for collection in task_collections:
            for task in collection:
                try:
                    # skipping any bugs that have this tag
                    if 'ct-rev' in task.bug.tags:
                        continue
                    # also skipping the bugs scalated by the support team.
                    if 'customersupport' in task.bug.tags:
                        continue
                    if [tag for tag in task.bug.tags if 'regression-' in tag]:
                        # change the class to highlight for any bug that has a regression- tag in it
                        table_row = '<tr class="highlight">\n'
                    else:
                        table_row = '<tr>\n'
	            table_row += "<td class=\"icon right\"><span alt=\"(undecided)\" title=\"Undecided\" class=\"sprite bug-%s\">&nbsp;</span></td>" % (task.importance.encode('utf-8').lower())
		    
                    table_row += '<td class=\"amount\">%s</td>' % task.bug.id
                    table_row += "<td><a href='http://launchpad.net/bugs/%s'>%s</a></td>\n" % (task.bug.id, escape(task.bug.title.encode('utf-8')))
	            table_row += "<td align=\"right\" style=\"padding-right: 5px\"></td>"
                    # maybe assignee should be a link to the person's launchpad page
                    package_name = re.sub('\ \(Ubuntu\)','', task.bug_target_display_name)
                    table_row += '<td><a href=\"https://bugs.launchpad.net/ubuntu/+source/%s">%s</td>\n' % (package_name.encode('utf-8'), package_name.encode('utf-8'))
                    importance = task.importance.encode('utf-8')
                    table_row += "<td class=\"importance%s\">%s</td>" % (importance.encode('utf-8').upper(), importance.encode('utf-8')) 
                    status = task.status.encode('utf-8')
		    table_row += "<td class=\"status%s\">%s</td>" % (status.encode('utf-8').upper().replace(" ",""), status.encode('utf-8'))
                    table_row += '<td id="release">'
                    affected_releases = []
                    for release in supported_releases:
                        target = ubuntu.getSeries(name_or_version=release.lower())
                        if has_target(task.bug, target):
                            affected_releases.append('%s%s' % (release[0], release[0]))
                    if affected_releases:
                        table_row += ', '.join(affected_releases)
                    else:
                        table_row += ''
                    table_row += '</td>\n'

                    if task.milestone:
                        table_row += '<td id="milestone">%s</td>\n' % task.milestone.name.encode('utf-8')
                    else:
                        table_row += '<td id="milestone"></td>\n'

                    assignee = task.assignee.display_name
                    try:
                        table_row += '<td id="assignee">%s</td>\n' % assignee.encode('utf-8')
                    except UnicodeDecodeError:
                        table_row += '<td id="assignee">%s</td>\n' % task.assignee.name
                    #table_row += "<td></td>"
                    try:
                        table_row += '<td id="date_assigned">%s</td>\n' % task.date_assigned[:10].encode('utf-8')
                    except TypeError:
                        table_row += '<td id="date_assigned">%s</td>\n' % task.date_assigned.strftime('%Y-%m-%d')
                    items = [tag for tag in task.bug.tags if 'regression-' in tag]
                    if len(items) > 0:
                        table_row += '<td id="regression">'
                        for item in items:
                            table_row += "%s " % item.encode('utf-8')
                        table_row += '</td>\n'
                    else:
                        table_row += '<td id="regression"></td>\n'
                    table_row += "</tr>"
                    table_row += "\n"
                    datafile.write(table_row)
                    # only count rows that show up on the report not hokey ones
                    counts['total'] = counts.setdefault('total', 0) + 1
                    counts['%s' % assignee] = counts.setdefault(assignee, 0) + 1
                except HTTPError, error:
                    print "There was an error with LP: #%s: %s" % (task.title.split(' ')[1].replace('#',''), error.content)
    elif line.strip() == "<!-- *** Last Paragraph Space *** -->":
        try: 
            datafile.write("A total of <b>%s</b> bug tasks are assigned to the <b>%s</b> team!<br><br>" % (counts['total'], team_name) )
        except KeyError:
            datafile.write("The <b>%s</b> team needs more to do! They have no bug tasks assigned to them.<br><br>" % team_name)
        for k,v in sorted(counts.items(), key=itemgetter(1), reverse=True):
            if k == 'total':
                continue
            if counts[k] == 1:
                datafile.write("\n<b>%s</b> has %s task assigned<br>" % (k.encode('utf-8'), counts[k]))
            else:
                datafile.write("\n<b>%s</b> has %s tasks assigned<br>" % (k.encode('utf-8'), counts[k]))
        datafile.write('<br>')
    elif line.strip() == "<!-- *** Updated on *** -->":
          date_now = datetime.utcnow()
          datafile.write("<strong>Updated on: %s</strong>" % date_now)
    else:
        datafile.write(line)
datafile.close()

if os.path.exists('/home/pedro/canonical-desktop-team-assigned-bug-tasks.html'):
    if os.path.exists('/srv/qa.ubuntu.com/reports/ubuntu-desktop/canonical-desktop-team-assigned-bug-tasks.html'):
        os.remove('/srv/qa.ubuntu.com/reports/ubuntu-desktop/canonical-desktop-team-assigned-bug-tasks.html')
    shutil.move('/home/pedro/canonical-desktop-team-assigned-bug-tasks.html', '/srv/qa.ubuntu.com/reports/ubuntu-desktop')
