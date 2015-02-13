#!/usr/bin/env python

# Script to generate an html page listing bugs in a basic table
import sys
import codecs
from optparse import OptionParser
import simplejson as json
from template import Template
from template.util import TemplateException, Literal

def loadfile(filename):
    in_file = open(filename, "r")
    text = in_file.read()
    in_file.close()
    return text

# TODO:  Parameterize this (load from /etc/arsenal/arsenal.conf)

def main():
    usage = '''
    %prog [options] <data-file.json>
    '''
    parser = OptionParser(usage=usage)

    parser.set_defaults(title = "Bug Listing")
    parser.set_defaults(tt2_dir = "/home/bryce/src/Arsenal/arsenal/web")

    parser.add_option('--show-source', action="store_true", dest="show_source",
                      help="display source package information" )
    parser.add_option('--show-assignee', action="store_true", dest="show_assignee",
                      help="include column showing the assignee")
    parser.add_option('--show-milestone', action="store_true", dest="show_milestone",
                      help="include column showing the targeted milestone")
    parser.add_option('--show-stats', action="store_true", dest="show_stats",
                      help="show details about bugs age, num comments, etc." )
    parser.add_option('--show-symptoms', action="store_true", dest="show_symptoms",
                      help="show any tags corresponding to X symptoms")
    parser.add_option('--show-tags', action="store_true", dest="show_tags",
                      help="show bug tags")
    parser.add_option('--show-last-message-age', action="store_true", dest="show_last_message_age",
                      help="show how many days since the bug last got a comment")
    parser.add_option('--show-patches', action="store_true", dest="show_patches",
                      help="show information about patches attached to the bug report")
    parser.add_option('--show-releases', action="store_true", dest="show_releases",
                      help="indicate which Ubuntu releases are tagged as affected")
    parser.add_option('--title', action="store", type="string", dest="title",
                      help="specify title for the page.  [Default '%default']")
    parser.add_option('--tt2-dir', action="store", type="string", dest="tt2_dir",
                      help="specify location of the templates directory.  [Default '%default']")

    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)

    columns = [
        { 'title': 'Bug',        'field': 'id',                'format': 'text',
          'link_url' : "http://bugs.launchpad.net/bugs/",      'link_field': "id" },
        { 'title': 'Summary',    'field': 'title',             'format': 'text' },
        { 'title': 'Importance', 'field': 'importance',        'format': 'ordered' },
        { 'title': 'Status',     'field': 'status',            'format': 'ordered' },
        ]

    if (options.show_releases):
        columns.append( { 'title': 'Releases',   'field': 'releases', 'format': 'array' } )

    if (options.show_symptoms):
        columns.append( { 'title': 'Chip',       'field': 'chip', 'format': 'array' } )
        columns.append( { 'title': 'Symptoms',   'field': 'symptoms', 'format': 'array' } )

    if (options.show_tags):
        columns.append( { 'title': 'Tags',       'field': 'tags', 'format': 'array' } )

    if (options.show_source):
        columns.append( { 'title': 'Package',    'field': 'target' } )

    if (options.show_assignee):
        columns.append( { 'title': 'Assignee',   'field': 'assignee',
                          'link_url' : "http://launchpad.net/~",
                          'link_field': "assignee" } )

    if (options.show_milestone):
        columns.append( { 'title': 'Milestone',  'field': 'milestone',
                          'link_url' : "https://launchpad.net/ubuntu/+milestone/",
                          'link_field': "milestone" } )

    if (options.show_stats):
        columns.append( { 'title': 'Dupes',      'field': 'dupes',            'format': 'integer',
                          'yellow' : 5, 'orange' : 10, 'red' : 20, } )
        columns.append( { 'title': 'Age',        'field': 'age',              'format': 'integer',
                          'yellow' : 5, 'orange' : 10, 'red' : 20, } )
        columns.append( { 'title': 'Last',       'field': 'last_message_age', 'format': 'integer',
                          'yellow' : 5, 'orange' : 10, 'red' : 20, } )
        columns.append( { 'title': 'Subs',       'field': 'num_subscribers',  'format': 'integer',
                          'yellow' : 5, 'orange' : 10, 'red' : 20, } )
        columns.append( { 'title': 'Cmts',       'field': 'num_comments',     'format': 'integer',
                          'yellow' : 25, 'orange' : 50, 'red' : 100, } )

    if (options.show_last_message_age):
        columns.append( { 'title': 'Last Msg',   'field': 'last_message_age', 'format': 'integer' } )

    if (options.show_patches):
        columns.append( { 'title': 'Sponsoring', 'field': 'sponsoring',       'format': 'text' } )
        columns.append( { 'title': 'Patch Age',  'field': 'patch_age',        'format': 'array' } )

    datafile = args[0]

    js = loadfile(datafile)
    if not js:
        sys.stderr.write("Error:  Content $datafile could not be loaded\n")
        exit(1)

    # Hack!  Disable unicode (breaks template-toolkit)
    try:
        js = js.replace('\u', '/U')
        data = json.loads(js)
    except:
        print "Error loading json data from %s" %(datafile)
        raise

    TEMPLATE_CONTENT = "templates/table.tt2"
    TEMPLATE_MAIN    = "templates/main.tt2"
    tt2 = Template(config = {
        'INCLUDE_PATH' : options.tt2_dir
        } )

    try:
        tt2_vars = {
            'table_name': 'bugs',
            'columns': columns,
            'sort_column': 'id',
            }
        if type(data) is list:
            tt2_vars['data'] = data
            last_updated = 'unknown'
        elif type(data) is dict:
            tt2_vars['data'] = data['bug_tasks']
            last_updated = data.get('timestamp-stop', 'unknown').split('.')[0]
        content = tt2.process(TEMPLATE_CONTENT, vars=tt2_vars)
        print tt2.process(TEMPLATE_MAIN, {
            'title': options.title,
            'content': content,
            'last_updated': last_updated
            } )

    except TemplateException, e:
        sys.stderr.write("ERROR(tt2): %s" % e)
        return 1

    except UnicodeEncodeError, e:
        sys.stderr.write("Unicode error: %s\n" %(e))
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
