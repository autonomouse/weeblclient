#!/usr/bin/python

import os
import sys
import re
import cgi
import cgitb
import json
from lpltk import LaunchpadService
from lpltk.LaunchpadService import LaunchpadServiceError

# TODO:
#   * Create a snazzy CSS for the page
#   * Highlight comments from the original reporter
#   * Highlight comments from a package maintainer
#   * Add a rightside bar (floating?) for the apport info (small text)
#   * Add a form for entering comments, status changes, etc.
#   * Add buttons for pasting in stock replies
#   * Add tags
#   * Add ubuntu animal icons to show releases affected
#   * horiz line between each comment
#   * Automatic linking of bug id's
#   * Automatic linking of git commits
#   * Automatic tests for bug report symptoms, quality and readiness for workflow steps
#   * Workflow advancement buttons (sub ubuntu-archive, forward upstream, etc.)
#   * Bug symptoms diagnostics (suggest stock replies for detected symptoms)
#   * Track viewing of messages and highlight new ones
#   * Add support for stock replies loaded from central site on per-package basis
#   * Display time since last reply from original reporter

def bug_dict(bug_id, cache=None):
    try:
        bug = lp.get_bug(bug_id)
    except LaunchpadServiceError, e:
        print "Service error"
        sys.exit(1)
    except KeyError, e:
        print "Error loading bug %s (is it private?)" %(e)
        sys.exit(1)

    print """
<head>
  <title>%s: %s</title>
</head>
<body>
""" %(bug_id, bug.title)

    notes = []
    if bug.private:
        # TODO: Need to be logged in to view private bugs
        notes.append(' [PRIVATE]')
    if bug.lpbug.latest_patch_uploaded:
        notes.append(' [PATCH %s]' %bug.lpbug.latest_patch_uploaded)

    re_spn = re.compile("^([^\s]+) ?\(?(Ubuntu|) ?([^\s]*?)\)?$")

    main_source_package = None

    tasks = {}
    for bug_task in bug.tasks:
        source_package_name = bug_task.bug_target_display_name
        distro = ''
        distro_version = ''
        target = ''

        m = re_spn.match(source_package_name)
        if m:
            source_package_name = m.group(1)
            distro = m.group(2)
            distro_version = m.group(3)

        task = {
            'source_package_name': source_package_name,
            'status':              bug_task.status,
            'importance':          bug_task.importance,
            'assignee':            '',
            'distro':              distro,
            'distro_version':      distro_version,
            'remote_bug':          '',
            'remote_package_name': '',
            }
        assignee = bug_task.assignee
        if assignee is not None:
            task['assignee'] = assignee.name
        if bug_task.bug_watch:
            task['remote_bug'] = bug_task.bug_watch.remote_bug
            target = 'upstream'
        if distro_version:
            target = distro_version
        elif distro:
            main_source_package = source_package_name  # hacky? just use last package in list?
            target = distro
            if bug_task.target and bug_task.target.upstream_product:
                task['remote_package_name'] = bug_task.target.upstream_product.name
        else:
            target = 'upstream'

        if source_package_name not in tasks:
            tasks[source_package_name] = {}
        tasks[source_package_name][target] = task

    bug_url = "https://bugs.launchpad.net/ubuntu/+source/%s/+bug/%s" %(main_source_package, bug_id)

    # Apport details we care about
    print "<div style='float:right;'>"
    print "<h3> System Information </h3>"
    print "<table>"
    for k in ['DistroVariant', 'DistUpgraded', 'UpgradeStatus',
              'MachineType', 'Architecture', 'GraphicsCard',
              'CompositorRunning', 'Renderer']:
        if k in bug.properties:
            print "<tr><td><b>%s:</b></td><td>%s</td></tr>" %(k, bug.properties[k])

    re_version = re.compile("^version\.")
    for k in bug.properties.keys():
        if re_version.search(k):
            [pkg, version] = bug.properties[k].split(' ')
            print "<tr><td>%s</td><td>%s</td></tr>" %(pkg, version)
    print "</table>"

    #print "<h3>Similar Bugs</h3>"
    #print "<table>"
    # TODO: Oops in launchpad (Bug #789383)
    #for similar_bug in bug_task.similar_bugs:
    #    print "<tr><td>%d</td><td>%s</td></tr>" %(similar_bug.id, similar_bug.title)
    #print "</table>"
    print "</div>"

    print "<h3>Bug: %s</h3>" %(bug_id)
    print "<h2>%s</h2>" %(bug.lpbug.title)  # TODO: bug.title doesn't display unicode chars
    print "<h3>Reported by: %s%s</h3>" %(bug.owner.display_name, ' '.join(notes))
    print

# TODO: Actions to take... stock replies... notes...
#       * Add as affected [project]
#       * Delete Core file and make public
    print "<p>"
    print "<a href=''>Convert to SRU</a> ~ "
    print "<a href=''>Convert to question</a> ~"
    print "<a href='%s/+duplicate'>Mark as duplicate</a>" %(bug_url)
    print "</p>"

    source_package_names = tasks.keys()
    source_package_names.sort()
    print "<table border='0' cellpadding='8' cellspacing='0'>"
    print "<tr><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td></tr>" %(
        'Target', 'Distro', 'Status', 'Importance', 'Assignee', 'Upstream')
    for pkg_name in source_package_names:
        for target, task in tasks[pkg_name].items():
            if target == 'upstream':
                continue
            upstream = ''
            distro = task['distro_version']
            if not distro:
                distro = task['distro']
            if 'upstream' in tasks[pkg_name].keys():
                upstream_task = tasks[pkg_name]['upstream']
                upstream = "%s project" %(pkg_name)
                if upstream_task['remote_bug']:
                    upstream = upstream_task['remote_bug']
            elif task['remote_package_name']:
                upstream_pkg_name = task['remote_package_name']
                if 'upstream' in tasks[upstream_pkg_name]:
                    upstream_task = tasks[upstream_pkg_name]['upstream']
                    if upstream_task['remote_bug']:
                        upstream = upstream_task['remote_bug']
                    else:
                        # TODO: In this case there is already an upstream task, but it
                        #       hasn't been linked to a bug url.  upstreamer needs to handle this.
                        upstream = "<a href='/cgi-bin/upstreamer.cgi?bug_id=%s'>Forward</a>" %(bug_id)
            else:
                upstream = "<a href='/cgi-bin/upstreamer.cgi?bug_id=%s'>Forward</a>" %(bug_id)

            # TODO: Some means to set these values (dynamically?)
            print "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %(
                task['source_package_name'],
                distro,
                task['status'],
                task['importance'],
                task['assignee'],
                upstream)
    print "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %(
        "<a href='%s/+distrotask'>+ package</a> " %(bug_url),
        "<a href='%s/+nominate'>+ release</a>" %(bug_url),
        '',
        '',
        '',
        "<a href='%s/+choose-affected-product'>+ upstream task</a> " %(bug_url))
    print "</table>"

    print
    print "<table cellpadding='8'><tr><td valign='top'>"
    print "<h3>Description:</h3>"

    # Description
    re_apport_info = re.compile("(?:ProblemType|dmi\.bios\.vendor|SourcePackage):\s+(.*)")
    re_binary_package = re.compile("^Binary package hint:")
    for section in bug.description.split('\n\n'):
        if re_binary_package.search(section):
            continue
        if re_apport_info.search(section):
            # Omit all the apport data, we'll display it more prettily later
            continue
        print "<pre>%s</pre>" %(section)
        print
    print "</td>"
    print "<td>&nbsp;</td>" # Spacer.  Ick.

    print "<td valign='top'><h3>Tags</h3>"
    print "<form>"
    official_bug_tags = ['regression', 'crash', 'freeze', 'corruption']
    for t in official_bug_tags:
        if t in bug.tags:
            print "  <input type='checkbox' checked> %s </input><br />" %(t)
        else:
            print "  <input type='checkbox'> %s </input><br />" %(t)
    for t in bug.tags:
        if t in official_bug_tags:
            continue
        print "  <input type='checkbox' checked> %s </input><br />" %(t)
    print "</form>"
    print "</td></tr></table>"

    just_provided_apport_info = False
    for message in bug.lpbug.messages:
        message_dict = None
        message_cache_filename = message.self_link.replace('/', '-')
        message_id = int(message_cache_filename.split('-').pop())
        if message_id < 1:
            continue

        object_filename = object_cache + '/' + message_cache_filename
        if os.path.isfile(object_filename):
            json_file = open(object_filename, 'r')
            message_dict = json.load(json_file)
            message_dict['cached'] = True
            json_file.close()

        elif len(message.content)>0:
            message_dict = {
                'id':           message_id,
                'date_created': message.date_created.strftime("%Y-%m-%d %H:%M"),
                'owner_name':   message.owner.display_name,
                'content':      message.content
                }

        if message_dict is not None:
            if message_dict['content'] == 'apport information':
                if just_provided_apport_info:
                    continue
                else:
                    just_provided_apport_info = True

            print "<p><b>%s</b> on %s  (#%d)</p>" %(
                message_dict['owner_name'],
                message_dict['date_created'],
                message_dict['id'])
            content = message_dict['content'].encode('utf-8')
            content = content.replace('\n', '<br>\n')
            print "<blockquote>%s</blockquote>\n" %(content)
            if 'cached' not in message_dict:
                json_file = open(object_filename, 'w')
                json_file.write(json.dumps(message_dict, indent=4))
                json_file.close()


if __name__ == '__main__':
    print "Content-Type: text/html; charset=utf-8\n\n"
    cgitb.enable()

    # We need to have a home location since not running as a user
    if not 'HOME' in os.environ:
        os.environ['HOME'] = '/var/cache/apache2/arsenal'
    object_cache = os.environ['HOME'] + "/objects"
    if not os.path.isdir(object_cache):
        os.mkdir(object_cache)

    try:
        lp = LaunchpadService(config={'read_only':True})
        d = lp.load_project("ubuntu")
    except LaunchpadServiceError, e:
        print e.msg
        sys.exit(1)

    form = cgi.FieldStorage()
    if form.has_key('bug_id'):
        bug_id = form['bug_id'].value
        bug_dict(bug_id, cache=object_cache)
    else:
        print "Please specify bug_id"
        pass

# TODO: Comment hiding
# TODO: Identify git commit's and offer to patchify them
# TODO: Identify patches and offer to autopackage them
# TODO: Include links/stock-replies to handy pages like bisection and backtrace directions
#        https://wiki.ubuntu.com/X/Backtracing
#        https://wiki.ubuntu.com/X/Troubleshooting/Freeze
#        https://wiki.ubuntu.com/Kernel/KernelBisection
#        http://kernel.ubuntu.com/~kernel-ppa/mainline/
#        http://git.kernel.org/?p=linux/kernel/git/ickle/drm-intel.git

# TODO:  Links to cgit tree for the package
