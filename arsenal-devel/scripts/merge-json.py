#!/usr/bin/python
#
# merge json files if they have the same keys else explode

import sys
import json
from optparse import OptionParser

usage = '''
%prog [options] <data-file> [data-file ...]
'''
parser = OptionParser(usage=usage)
parser.add_option(
    '-d', '--debug',
    action='store_true', dest='DEBUG', default=False,
    help='Enable debugging output')
(options, args) = parser.parse_args()

if len(args) < 1:
    parser.print_help()
    sys.exit(1)

data_files = args

keys = []
bug_tasks = []

for data_file in data_files:
    json_file = open(data_file, 'r')
    json_data = json.load(json_file)
    if not keys:
        keys = json_data['keys']
    if keys == json_data['keys']:
        for bugtask in json_data['bug_tasks']:
            bug_tasks.append(bugtask)
    else:
        sys.stderr.write("json files don't have the same keys\n")
        sys.exit(1)
    json_file.close()

report = {
    'keys'      : keys,
    'bug_tasks' : bug_tasks
}

print json.dumps(report, indent=4)
