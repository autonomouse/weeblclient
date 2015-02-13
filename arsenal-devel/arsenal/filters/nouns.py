#!/usr/bin/env python

import exceptions

from lpltk.attachments  import Attachments
from lpltk.bug          import Bug
from lpltk.bug_activity import Activity
from lpltk.bug_task     import BugTask
from lpltk.bug_tasks    import BugTasks
from lpltk.messages     import Messages
from lpltk.milestone    import Milestone
from lpltk.nominations  import Nominations
from lpltk.person       import Person

'''
Defines the "nouns" that make up a bug_task object.

This module provides a way to look up data on bug_tasks that are
provided by objects within the bug_task.

To add a new noun, select a unique name and add it as the key in the
noun table.  The value should be a dict that provides a lpltk class name
and the object lookup, obj, which should return the desired object given
an arbitrary bug_task "bt".
'''

nouns = {
    'bug_task':      {'class':BugTask,     'obj':lambda bt:bt},
    'assignee':      {'class':Person,      'obj':lambda bt:bt.assignee},
    'milestone':     {'class':Milestone,   'obj':lambda bt:bt.milestone},
    'related_tasks': {'class':BugTasks,    'obj':lambda bt:bt.related_tasks},

    'bug':           {'class':Bug,         'obj':lambda bt:bt.bug},
    'owner':         {'class':Person,      'obj':lambda bt:bt.bug.owner},
    'attachments':   {'class':Attachments, 'obj':lambda bt:bt.bug.attachments},
    'messages':      {'class':Messages,    'obj':lambda bt:bt.bug.messages},
    'messages_past_month': {'class':Messages,  'obj':lambda bt:bt.bug.messages_past_month},
    'nominations':   {'class':Nominations, 'obj':lambda bt:bt.bug.nominations},
    'activity':      {'class':Activity,    'obj':lambda bt:bt.bug.activity},
    }

class UnknownNoun(exceptions.Exception):
    def __init__(self, noun):
        self.noun = noun
    def __str__(self):
        return "Unknown noun %s" %(self.noun)

class UnknownProp(exceptions.Exception):
    def __init__(self, prop):
        self.prop = prop
    def __str__(self):
        return "Unknown property %s" %(self.prop)

def get_noun_property(bugtask, noun, prop):
    if noun not in nouns:
        raise UnknownNoun(noun)
    cls = nouns[noun]['class']
    obj = nouns[noun]['obj'](bugtask)
    method = getattr(cls, prop, None)
    if method is None:
        raise UnknownProp(prop)
    return method.__get__(obj, cls)
