#!/usr/bin/env python

from decimal                     import Decimal

def quote(msg):
    """
    Similar to urllib.quote but for glibs GMarkup
    @param msg: string to quote
    @returns: quoted string
    """
    msg = msg.replace('&', '&amp;')
    msg = msg.replace('<', '&lt;')
    msg = msg.replace('>', '&gt;')
    return msg

# o2str
#
# Convert a unicode, decimal.Decimal, or datetime object to a str.
#
def o2str(obj):
    retval = None
    if type(obj) == str:
        return obj
    elif type(obj) == unicode:
        return obj.encode('ascii', 'ignore')
    elif type(obj) == Decimal:
        return str(obj)
    elif type(obj) == list:
        new_list = []
        for item in obj:
            new_list.append(o2str(item))
            return new_list
    elif str(type(obj)) == "<type 'datetime.datetime'>":
        return obj.ctime()
    else:
        #print str(type(obj))
        return obj
