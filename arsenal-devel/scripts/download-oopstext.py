#!/usr/bin/env python
#
# Author: Brian Murray <brian@canonical.com>
# Copyright (C) 2010 Canonical, Ltd.
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along 
#
# This will script will search all the linux bug reports that are tagged
# apport-kerneloops for OopsText.txt attachments.  These will then be
# downloaded for processing locally.  Additionally, it is possible to preseed
# the OopsText files using a report on devpad.canonical.com.

import urllib
import re
from optparse import OptionParser

from launchpadlib.launchpad import Launchpad
from os import path

def get_oops_from_librarian():
    # On devpad.launchpad.net there is a report[1] of of some of the bugs with
    # OopsText.txt attached. It needs to be manually downloaded as it requires
    # single sign on logging in but it is a faster way to preseed the OopsTexts
    # than grabbing all of them using python-launchpadlib.
    # [1] https://devpad.canonical.com/~brian/bugs-with-kerneloops.html
    file = "bugs-with-kerneloops.html"

    bug_url = re.compile('<a href="http://launchpad.net/bugs/([0-9]+)')
    oops_number = re.compile('<a href="(http://launchpadlibrarian.net/[0-9]+/OopsText.txt)"')

    for line in open(file):
        if "http" in line:
            bug_url_match = bug_url.search(line)
            if bug_url_match:
                bug_number = bug_url_match.group(1)
            oops_number_match = oops_number.search(line)
            if oops_number_match:
                oops_url =  oops_number_match.group(1)
            target_file = '%s-OopsText.txt' % bug_number
            if not path.isfile(target_file):
                print "Downloading OopsText from %s" % ( bug_number )
                urllib.urlretrieve(oops_url, '%s-OopsText.txt' % bug_number)

if __name__ == '__main__':
    usage = '''
    %prog [OPTIONS]
    '''
    parser = OptionParser(usage=usage)
    parser.add_option(
        '-d', '--debug',
        action='store_true', dest='DEBUG', default=False,
        help='Enable debugging output')
    (options, args) = parser.parse_args()

    #if len(args) < 1:
    #    parser.print_help()
    #    sys.exit(1)

    # TODO: pull the values out into variables so it's easier to reuse
    args = {
        'tags' : [ 'apport-kerneloops' ],
        'tags_combinator' : 'Any',
        'order_by': '-datecreated',
    }

    # uncomment the librarian function to run it
    get_oops_from_librarian()
    # get the rest using launchpadlib
    launchpad = Launchpad.login_anonymously("Crash grabber", "edge")

    ubuntu = launchpad.distributions['ubuntu']

    package = ubuntu.getSourcePackage(name='linux')

    stop = False

    for task in package.searchTasks(**args):
        if stop == False:
            print "Checking LP: #%s" % task.bug.id
            for a in task.bug.attachments:
                if a.title == "OopsText.txt":
                    target_file = '%s-OopsText.txt' % task.bug.id
                    if not path.isfile(target_file):
                        print "Downloading OopsText from %s" % ( task.bug.id )
                        local_file = open(target_file, 'w')
                        hosted_file = a.data
                        hosted_file_content = hosted_file.open().read()
                        local_file.write(hosted_file_content)
                        local_file.close()
                        # only grab the first OopsText.txt attachment
                        continue
                    elif path.isfile(target_file):
                        stop = True
        elif stop == True:
            break
