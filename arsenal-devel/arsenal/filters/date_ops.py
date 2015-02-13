#!/usr/bin/env python

# "days_older_than"?
def max_days_since(dt, values):
    now = dt.now(dt.tzinfo)
    return (now - dt).days > int(values[0])

def min_days_since(dt, values):
    now = dt.now(dt.tzinfo)
    return (now - dt).days < int(values[0])

def later_than(dt, values):
    # TODO
    pass

def earlier_than(dt, values):
    # TODO
    pass

def on(dt, values):
    # TODO
    pass

