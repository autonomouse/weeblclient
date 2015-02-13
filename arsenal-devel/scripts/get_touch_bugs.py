#!/usr/bin/python -tt

# Copyright (C) 2012 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, print_function, absolute_import

import sys, os
import simplejson as json
from lpltk import LaunchpadService
from lpltk.LaunchpadService import LaunchpadServiceError
from genshi.template import TemplateLoader
from arsenal.arsenal_lib import ArsenalBug, bugtask_as_dict

INTERESTING_STATUS = ["New", "Incomplete", "In Progress", "Triaged", "Confirmed", "Fix Committed"]

def get_pillar_bugs(launchpad, pillarname):
    pillar = launchpad.projects[pillarname]
    #print pillar.searchTasks.__doc__
    bugtasks = pillar.searchTasks(status = INTERESTING_STATUS)
    return [launchpad.bugs[t.bug] for t in bugtasks]

def is_subscribed(bug, username):
#    print bug.description
#    print bug.web_link
    for u in  bug.subscriptions_collection:
        if u.person.name == username:
            return True
    return False

def subscribed_bugs(launchpad, pillar, user):
    bugtasks = get_pillar_bugs(launchpad, pillar)
#    print len(bugtasks)
    if user is None:
        return bugtasks
    return [bug for bug in bugtasks if is_subscribed(bug, user)]
#    print len(utouch_bugs)


def get_project_bugs(launchpad, bug_list, project):
    try:
        cur_bugs = get_pillar_bugs(launchpad, project)
        for bug in cur_bugs:
            if not project in bug_list:
                bug_list[project] = {}
            bug_list[project][bug.id] = True
    except Exception, e:
        print('  Error while processing:' % str(e))
            

def generate_buglist_array(launchpad, bug_list):
    result = []
    pillars = bug_list.keys()
    pillars.sort()
    processed_bugs = {}
    for pillar in pillars:
        bugs_in_pillar = []
        for bug_number in bug_list[pillar]:
            if bug_number in processed_bugs:
                break
            processed_bugs[bug_number] = True
            bug = launchpad.bugs[bug_number]
            #print('  %d: %s' % (bug_number, bug.title))
            tasks = []
            for task in bug.bug_tasks:
                if task.status == 'Invalid' or task.status == 'Unknown':
                    continue
                if task.assignee is None:
                    assignee = "Unassigned"
                else:
                    assignee = task.assignee.display_name
                if task.milestone is None:
                    milestone = 'No milestone'
                else:
                    milestone = task.milestone.name
                task_info = (task.bug_target_name, task.status, task.importance, milestone, assignee)
                tasks.append(task_info)
            bugs_in_pillar.append([bug.web_link, bug_number, bug.title, tasks])
        if len(bugs_in_pillar) > 0:
            result.append([pillar, bugs_in_pillar])
    return result

def generate_arsenal_bug_array(launchpad, bug_list):
    result = []
    pillars = bug_list.keys()
    pillars.sort()
    for pillar in pillars:
        for bug_number in bug_list[pillar]:
            bug = launchpad.bugs[bug_number]
            #print('  %d: %s' % (bug_number, bug.title))
            for task in bug.bug_tasks:
                if task.status == 'Invalid':
                    continue
                abug = ArsenalBug(bug, launchpad)
                result.append(bugtask_as_dict(abug, task))
    return result

def get_subscribed_bugs(launchpad, bug_list, username):
    user = launchpad.people[username]
    bugtasks = user.searchTasks(bug_subscriber=user, status=INTERESTING_STATUS)
    for task in bugtasks:
        pillar = task.bug_target_name.split(' ')[0] # Removes '(ubuntu)' suffixes etc.
#        print bug.target
        number = task.bug.id
        if pillar not in bug_list:
            bug_list[pillar] = {}
        bug_list[pillar][number] = True

def generate_html(bug_template_array):
    loader = TemplateLoader(os.path.dirname(__file__),
                            auto_reload=True
                            )
    imp_to_class = {'Unknown' : 'importance-unknown',
                    'Critical' : 'importance-critical',
                    'High' : 'importance-high',
                    'Medium' : 'importance-medium',
                    'Low' : 'importance-low',
                    'Wishlist' : 'importance-wishlist',
                    'Undecided' : 'importance-undecided'}
    
    script_dir = os.path.split(os.path.abspath(__file__))[0]
    template_dir = os.path.join(script_dir, '../reports/utouch/')
    tmpl = loader.load(os.path.join(template_dir, 'utouch_bug_template_flat.html'))
    stream = tmpl.generate(buglist=bug_template_array, imp_to_class=imp_to_class)
    return stream.render('xhtml')

def generate_json_text(arsenal_bug_list):
    report = {
              'keys'      : [ 'id', 'title', 'importance', 'status', 'target' ],
              'bug_tasks' : arsenal_bug_list
              }

    return json.dumps(report, indent=4)
    

def run_query(launchpad):
    json_output = False
    bug_list = {}
    utouch_user = 'utouch-bugs'
    utouch_project = 'canonical-multitouch'
    get_project_bugs(launchpad, bug_list, utouch_project)
    get_subscribed_bugs(launchpad, bug_list, utouch_user)
    if json_output:
        records = generate_arsenal_bug_array(launchpad, bug_list)
        out_txt = generate_json_text(records)
    else:
        bug_template_array = generate_buglist_array(launchpad, bug_list)
        out_txt = generate_html(bug_template_array)
    print(out_txt)

def print_subscriberpackages(launchpad, username):
    for p in get_subscriberpackages(launchpad, username):
        print(p)

def get_subscriberpackages(launchpad, username):
    user = launchpad.people[username]
    spackages = user.getBugSubscriberPackages()
    return [p.name for p in spackages]

def print_bug_info(bug):
    print('Repr:', repr(bug))
    print('ID:', bug.id)
    print('Self link:', bug.self_link)
    print('Title:', bug.title)
    print('\nBug subscribers')
    for p in bug.subscriptions_collection:
        print(p.person.name)

    print('Users affected')
    for c in bug.users_affected_collection:
        print(p.person.name)

    print('Users unaffected')
    for c in bug.users_unaffected_collection:
        print(p.person.name)

    for a in dir(bug):
        print(a)

def print_bug(launchpad):
    bug = launchpad.bugs[965477]
    print_bug_info(bug)
    print('Is there', is_subscribed(bug, 'utouch-bugs'))

def print_user(launchpad):
    user = launchpad.people['utouch-bugs']
    print(repr(user))
    for p in dir(user):
        print(p)
    bugtasks = user.searchTasks(bug_subscriber=user, status=INTERESTING_STATUS)
    for bug in bugtasks:
        print(bug.title)

if __name__ == '__main__':
    try:
        lp = LaunchpadService()
    except LaunchpadServiceError:
        sys.stderr.write("Error: Could not connect to Launchpad\n")
        sys.exit(1)
    run_query(lp.launchpad)
    #print_bug(launchpad)
    #print_user(launchpad)
    #print_subscriberpackages(lp.launchpad, 'utouch-bugs')
