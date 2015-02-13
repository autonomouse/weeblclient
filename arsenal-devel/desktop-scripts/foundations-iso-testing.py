#!/usr/bin/python
# script that creates a report for new bugs since a given date.

from launchpadlib.launchpad import Launchpad
from launchpadlib.errors import HTTPError
from launchpadlib.credentials import Credentials
from operator import attrgetter
import datetime
from datetime import datetime, date, timedelta
import time
import sys, os
import optparse
import shutil

def move_report(report):
    if os.path.exists(home + report):
        if os.path.exists(repository + report):
            os.remove(repository + report)
        shutil.move(home + report, repository)

def setup_page(page, since_when, title, packages):
    datafile = open(home + page, 'w')
    templatefile = open(template, 'r')
    bugcount = 0

    for line in templatefile:
        if line.strip() == "<!-- *** Title Space *** -->":
            datafile.write("Foundations bugs to Triage")
        elif line.strip() == "<!-- *** Title *** -->":
            datafile.write(title)
        elif line.strip() == "<!-- *** Table Header Space *** -->":
            datafile.write("<th></th><th>Bug Number</th><th>Package</th><th colspan=\"2\">Summary</th><th>Importance</th><th>Status</th><th>Users affected</th><th>Duplicates</th><th>Heat</th><th>Assignee</th>")
        elif line.strip() == "<!-- *** Table Body Space *** -->":
            for software in packages:
                source_package = ubuntu.getSourcePackage(name=software)
		# excluding bugs waiting to be retraced.
                for task in source_package.searchTasks(created_since=since_when, status='New', tags='iso-testing', tags_combinator='All', order_by='-heat'):
                    if "(Ubuntu)" in task.bug_target_display_name:
                        try:
                            table_row = "<tr>"
                            table_row += "<td class=\"icon right\"><span alt=\"(undecided)\" title=\"Undecided\" class=\"sprite bug-%s\">&nbsp;</span></td>" % (task.importance.encode('utf-8').lower())
                          
                            table_row += "<td class=\"amount\">%s</td>" % task.bug.id
			    table_row += "<td>%s</td>" % source_package.name
                            try:
                                table_row += "<td><a href='http://launchpad.net/bugs/%s'>%s</a></td>" % (task.bug.id, task.bug.title.encode('utf-8'))
                            except:
                                table_row += "<td><a href='http://launchpad.net/bugs/%s'>Can't decode title</a></td>" % (task.bug.id)
                            table_row += "<td align=\"right\" style=\"padding-right: 5px\"></td>"
                            table_row += "<td class=\"importance%s\">%s</td>" % (task.importance.encode('utf-8').upper(), task.importance.encode('utf-8'))
                            table_row += "<td class=\"status%s\">%s</td>" % (task.status.encode('utf-8').upper().replace(" ",""), task.status.encode('utf-8'))
                            table_row += "<td>%s</td>" % task.bug.users_affected_count
                            table_row += "<td>%s</td>" % task.bug.number_of_duplicates
                            table_row += "<td>%s</td>" % task.bug.heat
                            if task.assignee:
                                table_row += "<td><a href=\"http://launchpad.net/~%s\">%s</td>" % (task.assignee.name.encode('utf-8'), task.assignee.display_name.encode('utf-8'))
                            else:
                                table_row += "<td>None</td>"
                            table_row += "</tr>"
                            table_row += "\n"
                            bugcount+=1
                            highlist.append(task.bug)
                            datafile.write(table_row)
                            #print "ADDED ---> ", task.title.encode('utf-8'), task.bug.heat, task.bug.users_affected_count_with_dupes
                        except:
                            print "something went wrong"
        elif line.strip() == "<!-- *** Last Paragraph Space *** -->":
            datafile.write("<b>Packages being tracked:</b><br/>")
            for software in packages:
                datafile.write("%s <br/>" % software)
        elif line.strip() == "<!-- *** Updated on *** -->":
            date_now = datetime.utcnow()
            datafile.write("<strong>Updated on: %s</strong>" % date_now)
        else:
            datafile.write(line)
    datafile.close()
    move_report(os.path.basename(datafile.name))

home = os.getenv('HOME') + "/scripts/"
repository = '/srv/qa.ubuntu.com/reports/foundations-bugs/'
template = home + 'template.html' 
highlist = []
cachedir = os.path.expanduser("/home/pedro/.launchpadlib/cache/")
root = 'production'

if not os.path.exists(cachedir):
    os.makedirs(cachedir, 0700)

root = 'production'
version = "devel"
script_name = sys.argv[0].split("/")[-1].split('.')[0]

credfile = os.path.expanduser('/home/pedro/.launchpadlib/%s.cred' % script_name)
launchpad = Launchpad.login_with(script_name, service_root=root, launchpadlib_dir=cachedir, credentials_file=credfile, version=version)

ubuntu = launchpad.distributions["ubuntu"]

# get the list of packages in desktop-packages
team = launchpad.people['foundations-bugs']
desktop_packages = []
for p in team.getBugSubscriberPackages():
    desktop_packages.append(p.name)

setup_page('new-bugs-iso-testing.html', '2011-01-01', 'Foundations New bugs marked iso-testing', desktop_packages)
