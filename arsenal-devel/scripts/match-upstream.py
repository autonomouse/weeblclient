#!/usr/bin/env python

import pdb
import pycurl
import os
import re
import sys

from optparse import OptionParser
from pprint import PrettyPrinter
from urllib import urlencode

from arsenal.application import LaunchpadBugzillaApplication
from lpltk.bug import Bug

class MatchUpstream(LaunchpadBugzillaApplication):
    flagnames = ('DEBUG',)

    modifiers = ('max',)

    def run(self):
        searches = [
                [self.search_git_commits,
                 self.search_title_open,
                ],
                [self.search_title_all,
                ],
                [self.search_attachment_titles,
                ]
            ]

        self.bug = Bug(self.launchpad.service.launchpad, self.launchpad.bugid)

        print "Matching bug:", self.bug.title
        print "Maximum matches:", self.max

        pp = PrettyPrinter(indent=4)
        for searchlevel, searchfuncs in enumerate(searches):
            bugs = []
            print "Search level:", searchlevel

            for searchfunc in searchfuncs:
                matches = searchfunc()
                bugs.extend(matches[:self.max])

            if len(bugs) >= self.max:
                pp.pprint(bugs)
                print "Found enough bugs, stopping searching"
                return

        pp.pprint(bugs)

    def search_git_commits(self):
        bzbugs = []

        pattern = r'git.*([0-9a-f]{40})'
        regexp = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        for message in self.bug.lpbug.messages:
            result = regexp.findall(message.content)
            if not result:
                continue

            for commit in set(result):
                boolchart = []
                boolchart.append(('field0-0-0', 'longdesc'))
                boolchart.append(('type0-0-0', 'allwords'))
                boolchart.append(('value0-0-0', commit))
                bzbugs.extend(self.search_using_boolchart(boolchart))

        return bzbugs

    def search_title_all(self):
        return self.search_title(status='__all__')

    def search_title_open(self):
        return self.search_title(status='__open__')

    def search_title(self, status):
        formdata = [
            ('query_format', 'specific'),
            ('order', 'relevance desc'),
            ('bug_status', status),
            ('product', ''),
            ('content', self.bug.title)]

        listurl = self.sub_url_query('buglist.cgi?') + urlencode(formdata)
        header, response = self.bzadapter.get_response(listurl)
        bzbugs = self.parse_search_response(response)

        return bzbugs

    def search_attachment_titles(self):
        boolchart = []

        for index, attachment in enumerate(self.bug.attachments):
            boolchart.append(('field0-0-%d' % index, 'attachments.filename'))
            boolchart.append(('type0-0-%d' % index, 'equals'))
            boolchart.append(('value0-0-%d' % index, attachment.title))

        return self.search_using_boolchart(boolchart)

    def search_using_boolchart(self, boolchart):
        formdata = [('query_format', 'advanced'),]

        for key, value in boolchart:
            formdata.append((key, value))

        listurl = self.sub_url_query('buglist.cgi?') + urlencode(formdata)
        header, response = self.bzadapter.get_response(listurl)
        bzbugs = self.parse_search_response(response)

        return bzbugs

    def parse_search_response(self, response):
        pattern = r'<colgroup>(.*?)<\/colgroup>'
        regexp = re.compile(pattern, re.DOTALL)
        result = regexp.findall(response)
        if not result:
            return []
        colgroup = result[0]

        pattern = r'<col class="(.*?)">'
        regexp = re.compile(pattern, re.DOTALL)
        result = regexp.findall(colgroup)
        colnames = [colname.replace('_column', '').replace('bz_', '')
                    for colname in result]

        pattern = r'<tr class="bz_bugitem.*?">(.*?)<\/tr>'
        regexp = re.compile(pattern, re.DOTALL)
        result = regexp.findall(response)
        bugs = []
        for row in result:
            pattern = r'<td.*?>(.*?)<\/td>'
            regexp = re.compile(pattern, re.DOTALL)
            fields = regexp.findall(row)
            values = []
            for field in fields:
                pattern = r'<.*?>'
                regexp = re.compile(pattern, re.DOTALL)
                value = regexp.sub('', field).strip()
                values.append(value)
            bug = dict(zip(colnames, values))
            bug['link'] = self.sub_url_query('show_bug.cgi?id=' + bug['id'])
            bugs.append(bug)

        return bugs

if __name__ == "__main__":
    usage = '''
    %prog [options] <lp_url> <bugzilla_url>
    '''
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--debug',
        action='store_true', dest='DEBUG',
        default=False,
        help='Enable debugging output')
    parser.add_option('-u', '--user',
        action='store', type='string', dest='user',
        help='Bugzilla username')
    parser.add_option('-p', '--password',
        action='store', type='string', dest='password',
        help='Bugzilla password')
    parser.add_option('-m', '--max',
        action='store', type='int', dest='max', default=5,
        help='Maximum number of bugs to match')
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    flags = 0
    for flagname in MatchUpstream.flagnames:
        flags |= getattr(options, flagname) and \
                 getattr(MatchUpstream, flagname)

    modifiers = {
        'max' : options.max,
        }

    app = MatchUpstream('arsenal-match-upstream',
        lpurl=args[0],
        bzurl=args[1],
        bzuser=options.user,
        bzpassword=options.password,
        flags=flags,
        modifiers=modifiers)
    app.launch()

