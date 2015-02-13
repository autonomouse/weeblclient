#!/usr/bin/env python

import re

def contains_all(text, values):
    for phrase in values:
        if phrase not in text:
            return False
    return True

def contains_any(text, values):
    for phrase in values:
        if phrase not in text:
            return True
    return False

def contains_only(text, values):
    """Returns true if text is a strict subset of values"""
    for phrase in text:
        if phrase not in values:
            return False
    return True

def excludes_all(text, values):
    """Essentially !contains_any()"""
    for phrase in values:
        if phrase in text:
            return False
    return True

def excludes_any(text, values):
    """Essentially !contains_all()"""
    for phrase in values:
        if phrase not in text:
            return True
    return False

def matches_all_regex(text, values):
    """Must match all regex's specified in values"""
    for pattern in values:
        regex = re.compile(pattern)
        m = regex.matches(text)
        if not m:
            return False
    return True

def exclude_all_regex(text, values):
    """Must not match any of given regular expressions"""
    for pattern in values:
        regex = re.compile(pattern)
        m = regex.matches(text)
        if m:
            return False
    return True
