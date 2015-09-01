import re
import pytz
import string
import random
from datetime import datetime, timedelta
from dateutil import parser
from django.utils import timezone
from uuid import uuid4
from __init__ import __version__


def time_now():
    return timezone.now()


def generate_uuid():
    return str(uuid4())


def get_weebl_version():
    return __version__


def generate_random_string(n=10, uppercase=False):
    ascii = string.ascii_uppercase if uppercase else string.ascii_lowercase
    return "".join(random.choice(ascii) for i in range(n))


def generate_random_url(n=10):
    return "http://www.{}.com".format(generate_random_string(n))


def generate_random_date(limit_seconds=5000000000, when="any"):
    delta = timedelta(seconds=random.randint(0, limit_seconds))
    if when.lower() == "any":
        if random.randint(0, 9) % 2:
            when = "future"
        else:
            when = "past"
    if when.lower() == "future":
        timestamp = datetime.now() + delta
    else:
        timestamp = datetime.now() - delta
    return timestamp


def timestamp_as_string(timestamp, ts_format='%a %d %b %y %H:%M:%S'):
    timestamp_dt = normalise_timestamp(timestamp)
    return timestamp_dt.strftime(ts_format)


def normalise_timestamp(timestamp):
    if timestamp is None:
        return

    if type(timestamp) is str:
        return parser.parse(timestamp)
    else:
        return timestamp.replace(tzinfo=None)


def time_since(timestamp):
    timestamp_dt = normalise_timestamp(timestamp)
    return timezone.now() - pytz.utc.localize(timestamp_dt)


def time_difference_less_than_x_mins(timestamp, minutes):
    return time_since(timestamp) < timedelta(minutes=minutes)


def uuid_re_pattern():
    opt = "A-Fa-f0-9"
    uuid_pattern = "[" + opt + "]{8}-?[" + opt + "]{4}-?[" + opt + "]{4}-?["
    uuid_pattern += opt + "]{4}-?[" + opt + "]{12}"
    return uuid_pattern


def uuid_check(uuid):
    regex = re.compile("^" + uuid_re_pattern(), re.I)
    match = regex.match(uuid)
    return bool(match)


def pop(dictionary, fields):
    fields = list(fields) if fields is not list else fields
    for field in fields:
        try:
            dictionary.pop(field)
        except KeyError:
            pass
    return dictionary
