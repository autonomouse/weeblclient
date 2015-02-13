''' Miscellaneous Arsenal routines

This contains general purpose Arsenal code

Copyright (C) 2008 Canonical Lt.
Author: Bryce Harrington <bryce.harrington@ubuntu.com>

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
the full text of the license.
'''

import re, os, sys, string
import time, datetime
from urllib2 import URLError
import httplib2

from launchpadlib.launchpad import Launchpad
from launchpadlib.errors import HTTPError

# TODO:  Separate the Xorg-specific stuff into a separate library file

class ArsenalBugLite:
    # TODO:  Really want to wrapper a bug_task?
    def __init__(self, bug, launchpad):
        self.id          = bug.id
        self.bug         = bug
        self.title       = bug.title.encode('utf-8')
        try:
            self.description = bug.description.encode('utf-8')
        except UnicodeDecodeError:
            self.description = bug.description
        self.launchpad   = launchpad
        self.tags        = bug.tags

class ArsenalBug(ArsenalBugLite):
    ''' Wrapper around launchpadlibs bug object '''
    ubuntu_omittable_tags = ['omit', 'kubuntu', 'xubuntu', 'ppc']

    # TODO:  Really want to wrapper a bug_task?
    def __init__(self, bug, launchpad):
        ArsenalBugLite.__init__(self, bug, launchpad)
        #self.attachments = bug.attachments
        try:
            # LP raises "410: Gone" error if account is disabled
            self.owner = bug.owner
            if self.owner and self.owner.display_name:
                self.owner_firstname = self.owner.display_name.split(' ')[0]
        except:
            self.owner = None
            self.owner_firstname = ""

        #self.num_dupes = len(bug.duplicates)         # Expensive
        #self.num_subs  = len(bug.subscriptions)      # Expensive
        #self.num_affected = bug.users_affected_count # Expensive
        return

    def has_attachment(self, filename):
        # TODO:  Implement
        # TODO:  Maybe use regex for detection?
        return False

    def has_tag(self, tag):
        return tag in self.bug.tags

    def ubuntu_omittable(self):
        for tag in self.ubuntu_omittable_tags:
            if self.has_tag(tag):
                return True
        return False

    def has_patch(self):
        if self.bug.latest_patch_uploaded:
            return True
        return False

    # Searches title, description, and comments for given regular expression
    def has_text_match(self, re_text):
        regex = re.compile(re_text, re.IGNORECASE)
        # This routine seems to trip launchpad's 500 service errors a lot
        try:
            if regex.search(self.title) or regex.search(self.description):
                return True
            for m in self.bug.messages:
                if regex.search(m.content):
                    return True
            return False
        except:
            print("*** Exception *** Trying to scan bug comments and description")
        return False

    def has_upstream_task(self):
        distro_trackers = ['gentoo-bugs', 'redhat-bugs']
        for watch in self.bug.bug_watches:
            if watch.bug_tracker.name in distro_trackers:
                # Other distros don't count as upstreams
                continue
            upstream_bug = watch.remote_bug
            return True
        return False

    # Returns a list of source packages with tasks open for given distro
    def distro_task_sources(self, distro_name):
        distro_regex = re.compile("(.*) \("+distro_name+"\)")
        sources = [ ]
        for task in self.bug.bug_tasks:
            if task.is_complete:
                continue
            for match in distro_regex.findall(task.bug_target_display_name):
                sources.append(match)
        return sources

    # append_tags
    #
    # tags can be either a string or a list
    #
    def append_tags(self, tags):
        result   = False
        modified = False
        id       = self.id

        if type(tags) == list:
            self.bug = self.launchpad.bugs[id]
            tag_list = self.bug.tags
            for tag in tags:
                if not tag in self.bug.tags:
                    tag_list.append(tag)
                    modified = True

        if type(tags) == str:
            id = self.id
            if not tags in self.bug.tags:
                # Workaround bug #254901
                self.bug = self.launchpad.bugs[id]
                tag_list = self.bug.tags
                tag_list.append(tags)
                modified = True

        if modified:
                self.bug.tags = tag_list

                # Workaround bug #336866
                self.bug.lp_save()

                # Reload bug
                self.bug = self.launchpad.bugs[id]
                result = True

        return result

    def remove_tag(self, tag):
        if tag in self.bug.tags:
            # Workaround bug #254901
            tag_list = self.bug.tags
            tag_list.remove(tag)
            self.bug.tags = tag_list

            # Workaround bug #336866
            id = self.bug.id
            self.bug.lp_save()
            # Reload bug
            self.bug = self.launchpad.bugs[id]

            return True
        return False

    def append_description(self, text):
        self.bug.description = self.bug.description + "\n" + text

    def append_comment(self, message):
        # First doublecheck that we've not posted this comment before, so
        # automated calls to this routine don't end up spamming the reporter
        try:
            for m in self.bug.messages:
                if m.content == message:
                    print(" ---> Seems to already have this message")
                    return False
            self.bug.newMessage(subject = "Re: "+self.title, content = message)
            return True
        except:
            # TODO:  When this exception gets hit, it hardly ever goes through
            #        by just trying it again.  Maybe it needs a sleep added?
            print("*** Exception *** Trying to review messages")

        return False

    def subscribe(self, lp_id):
        person = self.launchpad.load(self.service_root + '~' + lp_id)
        self.bug.subscribe(person = person)
        print("bug " + str(self.id) + ": subscribing " + person.display_name)
        return True

    def dupe(self, dupe):
        self.bug.duplicate_of = dupe
        self.bug.lp_save()
#        # Reload bug
#        self.bug = self.launchpad.bugs[id]
        return True

    def unsubscribe(self, lp_id):
        # this currently does not work due to
        # https://bugs.launchpad.net/malone/+bug/281028
        print("bug " + str(self.bug.id) + ": unsubscribing " + lp_id.display_name)
        self.bug.unsubscribe(person=lp_id)

    def age(self):
        ''' Age of bug in days '''
        dlm = self.bug.date_created
        now = dlm.now(dlm.tzinfo)
        return (now - dlm).days

    def age_last_message(self):
        ''' Age of last comment to bug in days '''
        dlm = self.bug.date_last_message
        now = dlm.now(dlm.tzinfo)
        return (now - dlm).days

    def age_last_updated(self):
        ''' Age of last update to bug in days '''
        dlm = self.bug.date_last_updated
        now = dlm.now(dlm.tzinfo)
        return (now - dlm).days

map_kernel_version_to_ubuntu_release = {
    '3.2.0'  : { 'number' : '12.04', 'name'  : 'precise'  },
    '3.0.0'  : { 'number' : '11.10', 'name'  : 'oneiric'  },
    '2.6.38' : { 'number' : '11.04', 'name'  : 'natty'    },
    '2.6.33' : { 'number' : '10.10', 'name'  : 'maverick' },
    '2.6.32' : { 'number' : '10.04', 'name'  : 'lucid'    },
    '2.6.31' : { 'number' : '9.10',  'name'  : 'karmic'   },
    '2.6.28' : { 'number' : '9.04',  'name'  : 'jaunty'   },
    '2.6.27' : { 'number' : '8.10',  'name'  : 'intrepid' },
    '2.6.24' : { 'number' : '8.04',  'name'  : 'hardy'    },
    '2.6.22' : { 'number' : '7.10',  'name'  : 'gutsy'    },
    '2.6.20' : { 'number' : '7.04',  'name'  : 'feisty'   }
}

# Note: See http://kernel.ubuntu.com/~kernel-ppa/info/kernel-version-map.html
map_release_number_to_ubuntu_release = {
    '12.04'  : { 'kernel' : '3.2.0',  'name' : 'precise'  },
    '11.10'  : { 'kernel' : '3.0.0',  'name' : 'oneiric'  },
    '11.04'  : { 'kernel' : '2.6.38', 'name' : 'natty'    },
    '10.10'  : { 'kernel' : '2.6.35', 'name' : 'maverick' },
    '10.04'  : { 'kernel' : '2.6.32', 'name' : 'lucid'    },
    '9.10'   : { 'kernel' : '2.6.31', 'name' : 'karmic'   },
    '9.04'   : { 'kernel' : '2.6.28', 'name' : 'jaunty'   },
    '8.10'   : { 'kernel' : '2.6.27', 'name' : 'intrepid' },
    '8.04'   : { 'kernel' : '2.6.24', 'name' : 'hardy'    },
    '7.10'   : { 'kernel' : '2.6.22', 'name' : 'gutsy'    },
    '7.04'   : { 'kernel' : '2.6.20', 'name' : 'feisty'   }
}

# ubuntu_release_name_lookup
#
# Map from a kernel version to the name of a ubuntu release, this is used to 
# tag bugs.
#
def ubuntu_release_name_lookup(version):
    result = ''
    if result == '':
        m = re.search('([0-9]+)\.([0-9]+)\.([0-9]+)\-([0-9]+)\-(.*?)', version)
        if m != None:
            kver = "%s.%s.%s" % (m.group(1), m.group(2), m.group(3))
            if kver in map_kernel_version_to_ubuntu_release:
                result = map_kernel_version_to_ubuntu_release[kver]['name']

    if result == '':
        m = re.search('([0-9+)\.([0-9]+)', version)
        if m != None:
            dnum = m.group(1)
            if dnum in map_release_number_to_ubuntu_release:
                result = map_release_number_to_ubuntu_release[dnum]['name']

    return result

# find_distro_in_title
#
# Scan title for a pattern that looks like a distro name or version, and
# return the newest release version found.
#
def find_distro_in_title(ars_bug):
    results = []
    for rel_num, rel in map_release_number_to_ubuntu_release.iteritems():
        pat = "(%s|[^0-9\.\-]%s[^0-9\.\-])" %(rel['name'], rel_num.replace(".", "\."))
        regex = re.compile(pat, re.IGNORECASE)
        if regex.search(ars_bug.title):
            results.append(rel['name'])
    return results

# find_distro_in_description
#
# Look in the bugs description to see if we can determine which distro the 
# the user is running (hardy/intrepid/jaunty/karmic/lucid/etc.).
#
def find_distro_in_description(ars_bug):
    result = ''

    desc_lines = ars_bug.bug.description.split('\n')
    for line in desc_lines:
        # Sometimes there is a "DistroRelease:" line in the description.
        #
        m = re.search('DistroRelease:\s*(.*)', line)
        if (m != None):
            result = ubuntu_release_name_lookup(m.group(1))
            break

        # Sometimes there is the results of 'uname -a' or a dmesg in 
        # the description.
        #
        m = re.search('Linux version ([0-9]+)\.([0-9]+)\.([0-9]+)\-([0-9]+)\-(.*?) .*', line)
        if (m != None):
            kernel_version = "%s.%s.%s-%s-%s" % (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
            result = ubuntu_release_name_lookup(kernel_version)
            break

        if 'Description:' in line:
            m = re.search('Description:\s*([0-9]+\.[0-9]+)', line)
            if m != None:
                result = ubuntu_release_name_lookup(m.group(1))
                break

        if 'Release:' in line:
            m = re.search('Release:\s+([0-9]+\.[0-9]+)', line)
            if m != None:
                result = ubuntu_release_name_lookup(m.group(1))
                break

        # Sometimes it's just in the description
        #
        m = re.search('Ubuntu ((hardy|intrepid|jaunty|karmic|lucid|maverick)) [0-9]+\.[0-9]+', line)
        if (m != None):
            result = m.group(1)

    return result

# find_distro_in_attachments
#
# Look through the various files attached to the bug, by the original
# submitter/owner and see if we can determine the distro from there.
#
def find_distro_in_attachments(ars_bug):
    result = ''
    kernel_version = ''

    try:
        owner = ars_bug.owner.display_name.encode('utf-8')
        for attachment in ars_bug.bug.attachments_collection:
            # Short circuit the loop, if the attachment isn't from the bug
            # submitter, we don't really care.
            #
            if (attachment.message.owner.display_name.encode('utf-8') != owner):
                continue

            # Dmesg.txt / dmesg.log
            #
            m = re.search('[Dd]mesg.[txt|log]', attachment.title)
            if m != None:
                file = attachment.data.open()
                for line in file:
                    m = re.search('Linux version ([0-9]+)\.([0-9]+)\.([0-9]+)\-([0-9]+)\-(.*?) .*', line)
                    if (m != None):
                        kernel_version = "%s.%s.%s-%s-%s" % (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
                        break
                file.close()
                if kernel_version != '':
                    result = ubuntu_release_name_lookup(kernel_version)
                    break

            # alsa-info
            #
            if result == '':
                if 'alsa-info' in attachment.title:
                    file = attachment.data.open()
                    for line in file:
                        m = re.search('Kernel release:\s+([0-9]+)\.([0-9]+)\.([0-9]+)\-([0-9]+)\-(.*?)', line)
                        if (m != None):
                            kernel_version = "%s.%s.%s-%s-%s" % (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
                            break
                    file.close()
                    if kernel_version != '':
                        result = ubuntu_release_name_lookup(kernel_version)
                        break

            # xorg.0.log
            #
            if result == '':
                m = re.search('[Xx]org\.0\.log.*', attachment.title)
                if m != None:
                    file = attachment.data.open()
                    for line in file:
                        m = re.search('Current Operating System: Linux .* ([0-9]+)\.([0-9]+)\.([0-9]+)\-([0-9]+)\-(.*?) ', line)
                        if (m != None):
                            kernel_version = "%s.%s.%s-%s-%s" % (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
                            break
                    file.close()
                    if kernel_version != '':
                        result = ubuntu_release_name_lookup(kernel_version)
                        break

    except:
        pass # Just eat any exceptions

    return result

# determine_distro
#
# Try to figure out which distro version the bug submitter is running
# and has file the bug against.
#
def determine_distro(ars_bug):
    distro = find_distro_in_description(ars_bug)
    if (distro == ''):
        distro = find_distro_in_attachments(ars_bug)

    if (distro != ''):
        return distro
    return ''

# determine_distros
#
# Returns array of all distro versions that have been indicated
# in the bug report
#
def determine_distros(ars_bug):
    releases = find_distro_in_title(ars_bug)

    release = find_distro_in_description(ars_bug)
    if release and release not in releases:
        releases.append(release)

    release = find_distro_in_attachments(ars_bug)
    if release and release not in releases:
        releases.append(release)
    return releases


def is_triager(person):
    regex = re.compile("(bugs|bugcontrol|answer|tester|testing)")
    if not person:
        return False
    for team in person.super_teams:
        if regex.search(team.name):
            return True

# TODO:  Need a class specifically for backtraces
# TODO:  Review and adapt ideas from apport

def has_multiline_backtrace(text):
    '''
    Detects if there is a backtrace at least 3 levels deep
    '''
    regex_0 = re.compile('^#0 \w+')
    regex_1 = re.compile('^#1 0x\d+')
    regex_2 = re.compile('^#2 0x\d+')

    return regex_0.search(text) and \
           regex_1.search(text) and \
           regex_2.search(text)

def has_full_backtrace(text):
    '''
    Detects if backtrace contains parameter values
    '''
    regex = re.compile('^#\d+ 0x\d+ in \w+ \(\s+.*\)')
    regex_param = re.compile('^\s+\w+ = .+')

    return regex.search(text) and \
           regex_param.search(text)

def has_truncated_backtrace(text):
    '''
    Detects if the text has at least one line with a function name only
    '''
    regex = re.compile('^#\d+ 0x\d+ in \w+ \(\)$')
    return regex.search(text)

def has_xorg_backtrace(text):
    '''
    Matches the typical Xorg.0.log backtrace, even if no symbols are installed
    '''
    regex_symbolless = re.compile('^#\d+: [\w\/\.]+ \[0x[0-9a-f]+\]')
    regex_symbolled  = re.compile('^#\d+: [\w\/\.]+\(.+\) \[0x[0-9a-f]+\]')
    return regex_symbolless.search(text) or \
           regex_symbolled.search(text)

def has_backtrace(text):
    '''
    General purpose check for presence of a backtrace of any format
    '''
    return has_xorg_backtrace(text) or \
           has_multiline_backtrace(text)

def numerical_status(status):
    '''
    Prefix status strings with number (for sorting).
    Throws a KeyError exception if status is unmappable
    '''
    statuses = {
        "Invalid":                    "0 - Invalid",
        "Unknown":                    "0 - Unknown",
        "Won't Fix":                  "1 - Won't Fix",
        "Expired":                    "2 - Expired",
        "New":                        "3 - New",
        "Incomplete":                 "4 - Incomplete",
        "Confirmed":                  "5 - Confirmed",
        "Triaged":                    "6 - Triaged",
        "In Progress":                "7 - In Progress",
        "Fix Committed":              "8 - Fix Committed",
        "Fix Released":               "9 - Fix Released"
        }
    return statuses[status]

def numerical_importance(importance):
    '''
    Prefix importance strings with number (for sorting).
    Throws a KeyError exception if importance is unmappable
    '''
    importances = {
        'Critical':   '1 - Critical',
        'High':       '2 - High',
        'Medium':     '3 - Medium',
        'Low':        '4 - Low',
        'Wishlist':   '5 - Wishlist',
        'Undecided':  '6 - Undecided',
        'Unknown':    '7 - Unknown'
        }
    return importances[importance]

def is_launchpad_down(e):
    '''
    Internal Service Error.  This is often transient, so
    we could skip and go to the next bug, but this would
    leave the patch page in an inconsistent state, so
    instead lets just exit here.

    Bad Gateway.  Generally means Launchpad is unavailable,
    although this error is transient so we could just sleep
    a bit.  In this case we will skip execution and try later.

    Service unavailable.  Perhaps Launchpad is being
    upgraded or is otherwise Offline.  This seems to happen
    roughly once a day or so.

    Gateway Time-out.
    '''

    error_codes = [
        re.compile("HTTP Error (500): Internal Service Error.*"),
        re.compile("HTTP Error (502): (?:Bad Gateway|Proxy Error).*"),
        re.compile("HTTP Error (503): Service Unavailable.*"),
        re.compile("HTTP Error (504): Gateway Time-out,*"),
        ]

    code = 0
    reason = "%s" %(e)
    if hasattr(e, 'code'):
        code = e.code
    if hasattr(e, 'reason'):
        reason = "%s" %(e.reason)

    # Hackaround if code is not provided
    for regex in error_codes:
        m = regex.search(reason)
        if m:
            code = m.group(1)
            return True

    # TODO:  If fails many times in a row, send an email

    # Some other error occurred
    sys.stderr.write("Exception:  code %s\n" %(code))
    sys.stderr.write("            reason '%s'\n" %(reason))
    return False

def bugtask_as_dict(arsenal_bug, bugtask):
    try:
        url = "%s" %(bugtask.self)
    except:
        url = "UNKNOWN"
        #raise

    assignee = None
    if bugtask.assignee:
        assignee = bugtask.assignee.name.encode('utf-8')
    reporter = None
    karma = 0
    if arsenal_bug.owner:
        reporter = arsenal_bug.owner.name.encode('utf-8')
        karma = arsenal_bug.owner.karma
    date_closed = None
    if bugtask.date_closed:
        date_closed = bugtask.date_closed.ctime()
    date_fix_released = None
    if bugtask.date_fix_released:
        date_fix_released = bugtask.date_fix_released.ctime()

    source_pkg = string.replace(bugtask.bug_target_display_name, " (Ubuntu)", "")
    tag_list = bugtask.bug.tags
    bugtask_dict = {
        'id'               : arsenal_bug.id,
        '__url'            : url,
        'title'            : arsenal_bug.title,
        'date_created'     : bugtask.date_created.ctime(),
        'date_last_message': bugtask.bug.date_last_message.ctime(),
        'date_last_updated': bugtask.bug.date_last_updated.ctime(),
        'date_closed'      : date_closed,
        'date_fix_released': date_fix_released,
        'last_message_age' : arsenal_bug.age_last_message(),
        'is_complete'      : bugtask.is_complete,
        'assignee'         : assignee,
        'reporter'         : reporter,
        'target'           : source_pkg,
        'tags'             : tag_list,
        'status'           : numerical_status(bugtask.status),
        'importance'       : numerical_importance(bugtask.importance),
        'karma'            : karma,
        'affected users'   : bugtask.bug.users_affected_count,
        'heat'             : bugtask.bug.heat
        }
    # TODO:  Date reported, last commented, whether marked fixed upstream
    return bugtask_dict

