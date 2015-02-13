#!/usr/bin/env python
#
# Author: Brian Murray <brian@canonical.com>
#
# List the packages for which a team is the bug subscriber
#   additionally display whether or not the package has bug reporting
#   guidelines or an acknowledgement

from optparse import OptionParser

from lpltk import LaunchpadService

usage = '''
%prog --user <lp-user> --importance <IMPORTANCE> --status <STATUS>")
'''
parser = OptionParser(usage=usage)
parser.add_option(
    '-u', '--user',
    help='Launchpad user - person or team')
parser.add_option(
    '-s', '--status',
    help='Bug task status to filer on')
parser.add_option(
    '-i', '--importance',
    help='Bug task importance to filter on')
parser.add_option(
    '-t', '--tags',
    help='Tags to filter on')
(opt, args) = parser.parse_args()

params = {}

lp = LaunchpadService(config={'read_only': False})

user_name = opt.user

if opt.importance:
    params['importance'] = ['%s' % imp for imp in opt.importance.split(',')]
if opt.status:
    params['status'] = ['%s' % stat for stat in opt.status.split(',')]
if opt.tags:
    tag_list = ['%s' % tag for tag in opt.tags.split(',')]
else:
    tag_list = []

user = lp.launchpad.people[user_name]

count = 0

for sub_pkg in user.getBugSubscriberPackages():
    tasks = sub_pkg.searchTasks(**params)
    if len(tasks) > 0:
        print '%s' % sub_pkg.display_name.replace(' in Ubuntu', '')
    for task in tasks:
        print "  LP: #%s: %s" % (task.bug.id, task.bug.title)
        count += 1
print 'Total: %s' % count
