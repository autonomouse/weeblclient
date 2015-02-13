#!/usr/bin/env python

# TODO: Should these compare against all values?  Or just the first?

def less_than(arg, values):
    return int(arg) < int(values[0])

def greater_than(arg, values):
    return int(arg) > int(values[0])

def equal_or_less(arg, values):
    return int(arg) <= int(values[0])

def equal_or_greater(arg, values):
    return int(arg) >= int(values[0])

def equal_to(arg, values):
    return arg == values[0]

def not_equal_to(arg, values):
    return arg != values[0]

#
# Synonyms for convenience
#
lt = less_than
gt = greater_than
le = equal_or_less
ge = equal_or_greater
eq = equal_to
equals = equal_to
ne = not_equal_to
