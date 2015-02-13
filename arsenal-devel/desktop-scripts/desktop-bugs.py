#!/usr/bin/python

from launchpadlib.launchpad import Launchpad
from launchpadlib.errors import HTTPError
from launchpadlib.credentials import Credentials
from operator import attrgetter
import datetime
from datetime import datetime, date
import time
import sys, os
import optparse
import shutil

def move_report(report):
    if os.path.exists(home + report):
        if os.path.exists(repository + report):
            os.remove(repository + report)
        shutil.move(home + report, repository)
"""
def process_page(datafile, min_users_affected, min_heat, since_when, source_package):
    bugcount=0
    for task in source_package.searchTasks(created_since=since_when, status=['New', 'Incomplete', 'Confirmed', 'Triaged', 'In Progress', 'Fix Committed'], importance=['High','Critical','Medium','Low','Undecided'], order_by='-heat'):
        if "(Ubuntu)" in task.bug_target_display_name:
            if (task.importance == 'High' or task.importance == 'Critical') or (task.bug.heat >= min_heat and task.bug.users_affected_count_with_dupes >= min_users_affected):
                try:
                    table_row = "<tr>"
                    table_row += "<td class=\"icon right\"><span alt=\"(undecided)\" title=\"Undecided\" class=\"sprite bug-%s\">&nbsp;</span></td>" % (task.importance.encode('utf-8').lower())
                          
                    table_row += "<td class=\"amount\">%s</td>" % task.bug.id
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
                    print "ADDED --> ", task.title
                except HTTPError, error:
                    print "There was an error with bug %s: %s" % (task.title.split(' ')[1].replace('#',''), error)
            elif task.bug.heat < min_heat:
                print "SKIPPED - LAST ---> ", task.title, task.bug.heat, task.bug.users_affected_count_with_dupes 
                print "---> ", bugcount
                return
"""

def setup_page(page, min_users_affected, min_heat, since_when, title, packages):
    datafile = open(home + page, 'w')
    templatefile = open(template, 'r')
    bugcount = 0

    for line in templatefile:
        if line.strip() == "<!-- *** Title Space *** -->":
            datafile.write("Desktop Team Bugs Summary Page")
        elif line.strip() == "<!-- *** Title *** -->":
            datafile.write(title)
        elif line.strip() == "<!-- *** Table Header Space *** -->":
            datafile.write("<th></th><th>Bug Number</th><th colspan=\"2\">Summary</th><th>Importance</th><th>Status</th><th>Users affected</th><th>Duplicates</th><th>Heat</th><th>Assignee</th>")
        elif line.strip() == "<!-- *** Table Body Space *** -->":
            for software in packages:
                source_package = ubuntu.getSourcePackage(name=software)
#                process_page(datafile, min_users_affected, min_heat, since_when, source_package)
                for task in source_package.searchTasks(created_since=since_when, status=['New', 'Incomplete', 'Confirmed', 'Triaged', 'In Progress', 'Fix Committed'], importance=['High','Critical','Medium','Low','Undecided'], order_by='-heat'):
                    if "(Ubuntu)" in task.bug_target_display_name:
                        if (task.importance == 'High' or task.importance == 'Critical') or (task.bug.heat > min_heat and task.bug.users_affected_count_with_dupes >= min_users_affected):
                            try:
                                table_row = "<tr>"
                                table_row += "<td class=\"icon right\"><span alt=\"(undecided)\" title=\"Undecided\" class=\"sprite bug-%s\">&nbsp;</span></td>" % (task.importance.encode('utf-8').lower())
                          
                                table_row += "<td class=\"amount\">%s</td>" % task.bug.id
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
                                print "ADDED ---> ", task.title.encode('utf-8'), task.bug.heat, task.bug.users_affected_count_with_dupes
                            except HTTPError, error:
                                print "There was an error with bug %s: %s" % (task.title.split(' ')[1].replace('#',''), error)
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
repository = '/srv/qa.ubuntu.com/reports/ubuntu-desktop/'
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

# get the list of packages in desktop-bugs
team = launchpad.people['desktop-bugs']
desktop_packages = []
for p in team.getBugSubscriberPackages():
    desktop_packages.append(p.name)

#list of individual packages. 
other_packages = ['gwibber', 'telepathy-butterfly', 'telepathy-gabble', 'telepathy-haze', 'telepathy-idle', 'telepathy-indicator', 'xchat-indicator','network-manager', 'lightdm', 'network-manager-applet', 'libreoffice', 'language-selector', 'deja-dup', 'couchdb-glib', 'evolution-couchdb', 'banshee', 'jockey']
compiz = ['compiz']
mozilla = ['thunderbird', 'firefox']
unity = ['unity', 'nux', 'unity-place-applications', 'unity-place-files', 'libunity']
zeitgeist = ['zeitgeist', 'libzeitgeist', 'zeitgeist-filesystem', 'zeitgeist-sharp', 'zeitgeist-datasources', 'sezen', 'gnome-activity-journal', 'zeitgeist-extensions']
unity2d = ['unity-2d']
development = ['intltool', 'gettext', 'autoconf', 'automake', 'pkg-config', 'libtool']
indicators = ['indicator-application', 'indicator-appmenu', 'indicator-applet', 'indicator-sound', 'libindicate', 'evolution-indicator', 'indicator-datetime', 'indicator-me', 'indicator-messages', 'indicator-session']
software_center = ['software-center']

# (page, min_users_affected_count_with_dupes, min_heat, since_when, title, packages)
setup_page('index.html', 10, 50, '2011-01-01', 'Desktop Team Bugs Summary Page', desktop_packages)
setup_page('other-packages.html', 10, 50, '2011-01-01', 'Bugs in Other Packages', other_packages)
setup_page('mozilla-bugs.html', 10, 50, '2011-01-01', 'Bugs in Mozilla Packages', mozilla)
setup_page('compiz-bugs.html', 10, 50, '2011-01-01', 'Bugs in Compiz', compiz)
setup_page('unity-bugs.html', 10, 50, '2011-01-01','Bugs in Unity', unity)
setup_page('unity2d-bugs.html', 10, 50, '2011-01-01', 'Bugs in Unity 2D', unity2d)
setup_page('zeitgeist-bugs.html', 8, 50, '2011-01-01', 'Bugs in Zeitgeist', zeitgeist)
setup_page('development-bugs.html', 2, 10, '2011-01-01', 'Bugs in Development Packages', development)
setup_page('software-center-bugs.html', 8, 50, '2007-01-01', 'Bugs in Software Center', software_center)
setup_page('indicators-bugs.html', 10, 50, '2011-01-01', 'Bugs in Indicators Packages', indicators)

#Top Ten Worst Bugs Report

datafile = open(home + 'top-ten.html', 'w')
templatefile = open(template, 'r')
count = 0

for line in templatefile:
      if line.strip() == "<!-- *** Title Space *** -->":
          datafile.write("Desktop Team Bugs Summary Page")
      elif line.strip() == "<!-- *** Title *** -->":
          datafile.write("Top Ten Worst Bugs")
      elif line.strip() == "<!-- *** Table Header Space *** -->":
          datafile.write("<th></th><th>Bug Number</th><th colspan=\"2\">Summary</th><th>Importance</th><th>Status</th><th>Users affected</th><th>Duplicates</th><th>Heat</th><th>Assignee</th>")
      elif line.strip() == "<!-- *** Table Body Space *** -->":
          for bug in sorted(highlist, key=attrgetter('users_affected_count_with_dupes', 'heat'), reverse=True):
              if count <= 10:
                  for task in bug.bug_tasks:
                      if "(Ubuntu)" in task.bug_target_display_name:
                          try:
                              table_row = "<tr>"
                              table_row += "<td class=\"icon right\"><span alt=\"(undecided)\" title=\"Undecided\" class=\"sprite bug-%s\">&nbsp;</span></td>" % (task.importance.encode('utf-8').lower())
                              table_row += "<td class=\"amount\">%s</td>" % bug.id
                              try:
                                  table_row += "<td><a href='http://launchpad.net/bugs/%s'>%s</a></td>" % (bug.id, bug.title.encode('utf-8'))
                              except:
                                  table_row += "<td><a href='http://launchpad.net/bugs/%s'>Can't decode title</a></td>" % (bug.id)
                              table_row += "<td align=\"right\" style=\"padding-right: 5px\"></td>"
                              table_row += "<td class=\"importance%s\">%s</td>" % (task.importance.encode('utf-8').upper(), task.importance.encode('utf-8'))
                              table_row += "<td class=\"status%s\">%s</td>" % (task.status.encode('utf-8').upper().replace(" ",""), task.status.encode('utf-8'))
                              table_row += "<td>%s</td>" % bug.users_affected_count
                              table_row += "<td>%s</td>" % bug.number_of_duplicates
                              table_row += "<td>%s</td>" % bug.heat
                              if task.assignee:
                                  table_row += "<td><a href=\"http://launchpad.net/~%s\">%s</td>" % (task.assignee.name.encode('utf-8'), task.assignee.display_name.encode('utf-8'))
                              else:
                                  table_row += "<td>None</td>"
                              table_row += "</tr>"
                              table_row += "\n"
                              count+=1
                              datafile.write(table_row)
                              break
                          except HTTPError, error:
                              print "There was an error with bug %s: %s" % (bug.title.split(' ')[1].replace('#',''), error)
              else:
                  break
      elif line.strip() == "<!-- *** Updated on *** -->":
          date_now = datetime.utcnow()
          datafile.write("<strong>Updated on: %s</strong>" % date_now)
      else:
            datafile.write(line)
datafile.close()
move_report(os.path.basename(datafile.name))

