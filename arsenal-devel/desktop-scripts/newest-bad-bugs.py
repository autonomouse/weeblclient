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

def get_bug_tasks(package=None, release=None, begin=None):
    
    for task in package.searchTasks(tags=release, order_by='-datecreated', created_since=begin):
        if task.bug.heat > 100 and task.bug.number_of_duplicates > 1 and task.bug.users_affected_count > 1:
            print "-- https://bugs.launchpad.net/bugs/%s %s -- Package: %s -- Status: %s \n--> created on: %s -- users affected: %s -- duplicates: %s -- heat: %s" % (task.bug.id, task.bug.title.encode('utf-8'), package.display_name, task.status, task.bug.date_created, task.bug.users_affected_count, task.bug.number_of_duplicates, task.bug.heat)

cachedir = os.path.expanduser("~/.launchpadlib/cache/")
root = 'production'

if not os.path.exists(cachedir):
    os.makedirs(cachedir, 0700)

root = 'production'
version = "1.0"
script_name = sys.argv[0].split("/")[-1].split('.')[0]

credfile = os.path.expanduser('~/.launchpadlib/%s.cred' % script_name)
launchpad = Launchpad.login_with(script_name, service_root=root, launchpadlib_dir=cachedir, credentials_file=credfile, version=version)

ubuntu = launchpad.distributions["ubuntu"]
owner = ''

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("--package", help="Package to look for")
    parser.add_option("--since", help="Look for bug tasks created since %Y-%m-%d")
    parser.add_option("--team", help="Team to look for ")
    parser.add_option("--release", help="Release name specified in a tag")

    (opt, args) = parser.parse_args()

    if opt.since:
        begin = datetime.strptime(opt.since, "%Y-%m-%d")
    else:
        begin = date(2008, 01, 01)

    if opt.release:
        release = opt.release
    else:
        release = "natty"
        
    if opt.package:
        target = ubuntu.getSourcePackage(name=opt.package)
        get_bug_tasks(target,release,begin)
    elif opt.team:
        team = launchpad.people[opt.team]
        target = team.getBugSubscriberPackages()
        for p in target:
            get_bug_tasks(p,release,begin)

    """
        target = team.getBugSubscriberPackages()
        for package in target:
            get_bug_tasks(package)
    else:
        target = ubuntu.getSourcePackage(name=arg)
        get_bug_tasks(target)
        """
