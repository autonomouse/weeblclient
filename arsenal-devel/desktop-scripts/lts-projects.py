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
import re

def move_report(report):
    if os.path.exists(home + report):
        if os.path.exists(repository + report):
            os.remove(repository + report)
        shutil.move(home + report, repository)

def create_page(page, title, speed, boot, power):
    datafile = open(home + page, 'w')
    templatefile = open(template, 'r')
    bugcount = 0

    for line in templatefile:
        if line.strip() == "<!-- *** Title Space *** -->":
            datafile.write("Desktop Team Bugs Summary Page")
        elif line.strip() == "<!-- *** Title *** -->":
            datafile.write(title)
        elif line.strip() == "<!-- *** Collapsable1 *** -->":
            datafile.write("<h2>Boot Speed</h2><div class=\"collapsable\", id=\"div_bugs_speed\">")
	elif line.strip() == "<!-- *** ProgressBar1 *** -->":
	    opentasks = speed.searchTasks(status=['Fix Released','Invalid', 'Incomplete', 'New', 'Triaged', 'Confirmed', 'Fix Committed', 'Won\'t Fix', 'In Progress'] , omit_targeted=False, order_by='-heat')
	    opentasks = int(opentasks._wadl_resource.representation['total_size'])
	    closedtasks = speed.searchTasks(status=['Fix Released','Invalid', 'Won\'t Fix'] , omit_targeted=False, order_by='-heat')
	    closedtasks = int(closedtasks._wadl_resource.representation['total_size'])
   	    percent=(1.0*closedtasks/opentasks)*100
	    datafile.write("var bar = new ProgressBar('dynamic_progress_bar_full1', 'dynamic_progress_bar_empty1', 522, 0, %s, 1);" % (percent))
        elif line.strip() == "<!-- *** Table Header Space *** -->":
            datafile.write("<th></th><th>Bug Number</th><th colspan=\"2\">Summary</th><th>Source</th><th>Importance</th><th>Status</th><th>Users affected</th><th>Duplicates</th><th>Heat</th><th>Assignee</th>")
        elif line.strip() == "<!-- *** Table Body Space *** -->":
            for t in speed.searchTasks(omit_targeted=False, order_by='-heat'):
		for task in t.related_tasks:
                    if task.status == 'Triaged' or task.status == 'Confirmed' or task.status == 'Incomplete' or task.status == 'Fix Committed' or task.status == 'In Progress':
                        try:
                            table_row = "<tr>"
                            table_row += "<td class=\"icon right\"><span alt=\"(undecided)\" title=\"Undecided\" class=\"sprite bug-%s\">&nbsp;</span></td>" % (task.importance.encode('utf-8').lower())
                        
                            table_row += "<td class=\"amount\">%s</td>" % task.bug.id
                            try:
                                table_row += "<td><a href='http://launchpad.net/bugs/%s'>%s</a></td>" % (task.bug.id, task.bug.title.encode('utf-8'))
                            except:
                                table_row += "<td><a href='http://launchpad.net/bugs/%s'>Can't decode title</a></td>" % (task.bug.id)
                            table_row += "<td align=\"right\" style=\"padding-right: 5px\"></td>"
                            package_name = re.sub('\ \(Ubuntu Precise\)','', task.bug_target_display_name)
                            table_row += '<td><a href=\"https://bugs.launchpad.net/ubuntu/+source/%s">%s</td>\n' % (package_name.encode('utf-8'), package_name.encode('utf-8'))
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
                            datafile.write(table_row)
                        except HTTPError, error:
                            print "There was an error with bug %s: %s" % (task.title.split(' ')[1].replace('#',''), error)
        elif line.strip() == "<!-- *** EndCollapsable1 *** -->":
            datafile.write("</div>")
        elif line.strip() == "<!-- *** Collapsable2 *** -->":
            datafile.write("<h2>Power Consumption</h2><div class=\"collapsable\", id=\"div_bugs_power\">")
        elif line.strip() == "<!-- *** ProgressBar2 *** -->":
	    opentasks = power.searchTasks(status=['Fix Released','Invalid', 'Incomplete', 'New', 'Triaged', 'Confirmed', 'Fix Committed', 'Won\'t Fix', 'In Progress'] , omit_targeted=False, order_by='-heat')
	    opentasks = int(opentasks._wadl_resource.representation['total_size'])
	    closedtasks = power.searchTasks(status=['Fix Released','Invalid', 'Won\'t Fix'] , omit_targeted=False, order_by='-heat')
	    closedtasks = int(closedtasks._wadl_resource.representation['total_size'])
   	    percent=(1.0*closedtasks/opentasks)*100
	    datafile.write("var bar = new ProgressBar('dynamic_progress_bar_full2', 'dynamic_progress_bar_empty2', 522, 0, %s, 1);" % (percent))
        elif line.strip() == "<!-- *** Table Header Space2 *** -->":
            datafile.write("<th></th><th>Bug Number</th><th colspan=\"2\">Summary</th><th>Source</th><th>Importance</th><th>Status</th><th>Users affected</th><th>Duplicates</th><th>Heat</th><th>Assignee</th>")
        elif line.strip() == "<!-- *** Table Body Space2 *** -->":
            for t in power.searchTasks(omit_targeted=False, order_by='-heat'):
		for task in t.related_tasks:
                    if task.status == 'Triaged' or task.status == 'Confirmed' or task.status == 'Incomplete' or task.status == 'Fix Committed' or task.status == 'In Progress':
                        try:
                            table_row = "<tr>"
                            table_row += "<td class=\"icon right\"><span alt=\"(undecided)\" title=\"Undecided\" class=\"sprite bug-%s\">&nbsp;</span></td>" % (task.importance.encode('utf-8').lower())
                        
                            table_row += "<td class=\"amount\">%s</td>" % task.bug.id
                            try:
                                table_row += "<td><a href='http://launchpad.net/bugs/%s'>%s</a></td>" % (task.bug.id, task.bug.title.encode('utf-8'))
                            except:
                                table_row += "<td><a href='http://launchpad.net/bugs/%s'>Can't decode title</a></td>" % (task.bug.id)
                            table_row += "<td align=\"right\" style=\"padding-right: 5px\"></td>"
                            package_name = re.sub('\ \(Ubuntu Precise\)','', task.bug_target_display_name)
                            table_row += '<td><a href=\"https://bugs.launchpad.net/ubuntu/+source/%s">%s</td>\n' % (package_name.encode('utf-8'), package_name.encode('utf-8'))
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
                            datafile.write(table_row)
                        except HTTPError, error:
                            print "There was an error with bug %s: %s" % (task.title.split(' ')[1].replace('#',''), error)  
        elif line.strip() == "<!-- *** EndCollapsable2 *** -->":
            datafile.write("</div>")
        elif line.strip() == "<!-- *** Collapsable3 *** -->":
            datafile.write("<h2>Flicker-Free Boot</h2><div class=\"collapsable\", id=\"div_bugs_boot\">")
        elif line.strip() == "<!-- *** ProgressBar3 *** -->":
	    opentasks = boot.searchTasks(status=['Fix Released','Invalid', 'Incomplete', 'New', 'Triaged', 'Confirmed', 'Fix Committed', 'Won\'t Fix', 'In Progress'] , omit_targeted=False, order_by='-heat')
            opentasks = int(opentasks._wadl_resource.representation['total_size'])
	    closedtasks = boot.searchTasks(status=['Fix Released','Invalid', 'Won\'t Fix'] , omit_targeted=False, order_by='-heat')
            closedtasks = int(closedtasks._wadl_resource.representation['total_size'])
   	    percent=(1.0*closedtasks/opentasks)*100
	    datafile.write("var bar = new ProgressBar('dynamic_progress_bar_full3', 'dynamic_progress_bar_empty3', 522, 0, %s, 1);" % (percent))
        elif line.strip() == "<!-- *** Table Header Space3 *** -->":
            datafile.write("<th></th><th>Bug Number</th><th colspan=\"2\">Summary</th><th>Source</th><th>Importance</th><th>Status</th><th>Users affected</th><th>Duplicates</th><th>Heat</th><th>Assignee</th>")
        elif line.strip() == "<!-- *** Table Body Space3 *** -->":
            for t in boot.searchTasks(omit_targeted=False, order_by='-heat'):
		for task in t.related_tasks:
                    if task.status == 'Triaged' or task.status == 'Confirmed' or task.status == 'Incomplete' or task.status == 'Fix Committed' or task.status == 'In Progress':
                        try:
                            table_row = "<tr>"
                            table_row += "<td class=\"icon right\"><span alt=\"(undecided)\" title=\"Undecided\" class=\"sprite bug-%s\">&nbsp;</span></td>" % (task.importance.encode('utf-8').lower())
                            table_row += "<td class=\"amount\">%s</td>" % task.bug.id
                            try:
                                table_row += "<td><a href='http://launchpad.net/bugs/%s'>%s</a></td>" % (task.bug.id, task.bug.title.encode('utf-8'))
                            except:
                                table_row += "<td><a href='http://launchpad.net/bugs/%s'>Can't decode title</a></td>" % (task.bug.id)
                            table_row += "<td align=\"right\" style=\"padding-right: 5px\"></td>"
                            package_name = re.sub('\ \(Ubuntu Precise\)','', task.bug_target_display_name)
                            table_row += '<td><a href=\"https://bugs.launchpad.net/ubuntu/+source/%s">%s</td>\n' % (package_name.encode('utf-8'), package_name.encode('utf-8'))
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
                            datafile.write(table_row)
                        except HTTPError, error:
                            print "There was an error with bug %s: %s" % (task.title.split(' ')[1].replace('#',''), error)  
        elif line.strip() == "<!-- *** EndCollapsable3 *** -->":
            datafile.write("</div>")
        elif line.strip() == "<!-- *** Updated on *** -->":
            date_now = datetime.utcnow()
            datafile.write("<strong>Updated on: %s</strong>" % date_now)
        else:
            datafile.write(line)
    datafile.close()
    move_report(os.path.basename(datafile.name))

home = os.getenv('HOME') + "/scripts/"
repository = '/srv/qa.ubuntu.com/reports/ubuntu-desktop/'
template = home + 'lts-projects-template.html' 
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

speed = launchpad.projects["ubuntu-boot-speed"]
boot = launchpad.projects["ubuntu-flicker-free-boot"]
power = launchpad.projects["ubuntu-power-consumption"]


create_page('lts-projects.html', 'LTS Projects', speed, boot, power)
