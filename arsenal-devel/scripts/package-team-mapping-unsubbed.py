#!/usr/bin/python
# Author: Brian Murray <brian@canonical.com>
# Copyright (C) 2012 Canonical, Ltd.
# License: GPLv3
#
# compare the list of packages assigned to a team in the package to team
# mapping csv file and the packages to which a team is subscribed in Launchpad
# and print the packages to which the team is not subscribed

import optparse

from lpltk import LaunchpadService
from subprocess import Popen, PIPE

if __name__ == '__main__':

    parser = optparse.OptionParser(usage="usage: %prog --team team")

    parser.add_option('--team', help='Launchpad team name')
    parser.add_option('--csvteam', help='CSV team team')
    parser.add_option('--rmadison', help='look up package with rmadison',
        action='store_true')

    (opt, args) = parser.parse_args()

    lp = LaunchpadService(config={'read_only': False})

    team = lp.launchpad.people[opt.team]

    packages = [package.name for package in team.getBugSubscriberPackages()]

    unsubbed = []

    csvfile = open('../reports/package-team-mapping.csv', 'r')

    for line in csvfile.readlines():
        if not opt.csvteam in line:
            continue
        package = line.split(',')[0]

        if package not in packages:
            unsubbed.append(package)

    unsubbed.sort()

    for unsub_pkg in unsubbed:
        print('%s not subscribed to %s' % (opt.team, unsub_pkg))
        if not opt.rmadison:
            continue
        ubuntu_results = Popen(["rmadison", unsub_pkg],
            stdout=PIPE).communicate()[0]
        print("%s" % ubuntu_results)
