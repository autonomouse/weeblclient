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


def time_since(timestamp):
    if timestamp is None:
        return

    if type(timestamp) is not datetime:
        timestamp_dt = parser.parse(timestamp)
    else:
        timestamp_dt = timestamp.replace(tzinfo=None)
    return timezone.now() - pytz.utc.localize(timestamp_dt)


def time_difference_less_than_x_mins(timestamp, minutes):
    return time_since(timestamp) < timedelta(minutes=minutes)


def uuid_check(uuid):
    opt = "A-Fa-f0-9"
    uuid_pattern = "^[" + opt + "]{8}-?[" + opt + "]{4}-?[" + opt + "]{4}-?["
    uuid_pattern += opt + "]{4}-?[" + opt + "]{12}"
    regex = re.compile(uuid_pattern, re.I)
    match = regex.match(uuid)
    return bool(match)
