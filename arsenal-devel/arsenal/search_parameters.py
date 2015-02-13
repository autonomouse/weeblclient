#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils.config import Config
from utils.lists import to_list

class SearchParameters(Config):
    _searchTaskDefaults = {
        'affected_user':         None,
        'assignee':              None,
        'bug_commenter':         None,
        'bug_reporter':          None,
        'bug_subscriber':        None,
        'bug_supervisor':        None,
        'component':             None,
        'created_since':         None,
        'has_cve':               None,
        'has_no_package':        None,
        'has_patch':             None,
        'importance':            None,
        'linked_blueprints':     None,
        'max_days_since_modified': None,
        'milestone':             None,
        'modified_since':        None,
        'nominated_for':         None,
        'omit_duplicates':       None,
        'omit_targeted':         None,
        'order_by':              None,
        'owner':                 None,
        'search_text':           None,
        'status':                [],
        'status_upstream':       None,
        'structural_subscriber': None,
        'tags':                  [],
        'tags_combinator':       'All',
        }

    def __init__(self, filename, lines=None):
        # Load in default search parameters
        for key, value in self._searchTaskDefaults.items():
            self.__dict__[key] = value

        # Perhaps these could be in a 'criteria' child dict?
        self.name = None
        self.data_dir = '/tmp'
        self.cache_dir = '/tmp'
        self.app_name = 'arsenal'
        self.distribution = 'ubuntu'

        # These can probably be dropped
        self.max_days_since_modified = None

        self.require = {}
        self.source = {}
        self.exclude = {}

        self.quick = False # TODO: This isn't descriptive enough; 'lossy' option? brief? concise? detailed?
#        self.read_only = True         # -R/-w
#        self.quiet = False            # -q/-v
#        self.force_reload = False     # -r/-u
#        self.include_private = False  # -p/-P

        Config.__init__(self, filename, lines=lines)

        if self.name is None:
            if filename:
                import os.path
                name = os.path.basename(filename.replace('.search',''))
                self.name = name
            else:
                self.name = 'test'

        max_days_since_modified = self.require.get('max_days_since_modified')
        if max_days_since_modified:
            import datetime
            now = datetime.datetime.utcnow()
            delta = datetime.timedelta(days=int(max_days_since_modified))
            self.require['modified_since'] = now - delta
            del self.require['max_days_since_modified']

    def criteria(self, lp):
        '''Provides one or more sets of search criteria.

        Provides the set of parameters to pass directly to the lpltk
        search_tasks() routine for retrieving bug tasks.  Use of
        wildcards or multi-value parameters in searches can require
        multiple launchpad calls to gather all the required data; for
        that reason, this routine returns a list of criteria.

        Callers should iterate through this list and group all the
        resulting data together.
        '''
        criteria_list = [{}]
        for key, default in self._searchTaskDefaults.items():
            value = self.require.get(key, default)
            if not value:
                continue
            if type(default) is list:
                for data in criteria_list:
                    # If launchpad expects a list, send a list
                    data[key] = to_list(value)
            elif type(value) in (str, unicode):
                values = value.split(', ')
                new_values = []
                for value in values:
                    if key == 'assignee':
                        # Wildcard means include members of team
                        people = []
                        if value[-2:] == '.*':
                            # Double wildcard means include recursively
                            if value[-4:] == '.*.*':
                                people = lp.get_team_participants(value[:-4])
                            else:
                                people = lp.get_team_members(value[:-2])
                        else:
                            people = [ lp.person(value) ]
                        for person in people:
                            new_values.append(person.uri)
                        continue
                    elif key == 'nominated_for':
                        # TODO: Look up distro name and return distro obj
                        new_values.append(
                            "http://ubuntu.com/ubuntu/%s/" %(value))

                    # TODO: Expand this out to a proper macro substitution system
                    if value == u'${current_ubuntu_release_codename}':
                        # TODO: Retrieve from launchpad or cache
                        new_values.append('quantal')
                    elif value == u'${current_ubuntu_development_codename}':
                        # TODO: Retrieve from launchpad or cache
                        new_values.append('raring')
                    elif value == u'${original_reporter_name}':
                        # TODO: Get the original bug reporter's name
                        new_values.append('nobody')
                    else:
                        new_values.append(value)

                values = new_values

                for data in criteria_list:
                    data[key] = values[0]

                # If launchpad doesn't expect a list, and we have a list,
                # then we need to set up multiple search criteria sets.
                if len(values)>1:
                    for v in values[1:]:
                        new_criteria_list = []
                        # Create a new copy of all criteria sets for each additional value
                        for data in criteria_list:
                            new_data = data.copy()
                            new_data[key] = v
                            new_criteria_list.append(new_data)
                        criteria_list.extend(new_criteria_list)
            else:
                data[key] = value

        # Convert criteria into the format(s) launchpad expects
        for data in criteria_list:
            if 'tags' not in data.keys() or len(data['tags']) == 0:
                del data['tags_combinator']

        return criteria_list

if __name__ == "__main__":
    data = """
name = config_test
#app_name = arsenal
distribution = ubuntu

source.packages = xorg, xdiagnose
require.tags = precise, oneiric, natty
require.max_days_since_modified=7

quick = True
#quiet = False
"""
    sp = SearchParameters(None, lines=data)
    #print(sp)

    print(sp.criteria)

# vi:set ts=4 sw=4 expandtab:
