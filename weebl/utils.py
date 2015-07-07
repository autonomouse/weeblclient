import re
import pytz
import string
import random
from datetime import datetime, timedelta
from dateutil import parser
from django.utils import timezone
from uuid import uuid4

def time_now():
    return timezone.now()

def generate_uuid():
    return str(uuid4())

def generate_random_string(n=10, uppercase=False):
    ascii = string.ascii_uppercase if uppercase else string.ascii_lowercase
    return "".join(random.choice(ascii) for i in range(n))

def generate_random_url(n=10):
    return "http://www.{}.com".format(generate_random_string(n=8))

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
    uuid_pattern = "^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}"
    uuid_pattern += "-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z"
    regex = re.compile(uuid_pattern, re.I)
    match = regex.match(uuid)
    return bool(match)

# The following will be removed in the isOILup/views branch:

import os
from exceptions import InvalidConfig
from six.moves import configparser

_config = []


def find_config(conf=None):
    """Finds config file, allowing users to specify config via CLI or
    environment variable.  If neither, default config is returned

    :param conf: str path to specified config file.

    :returns: str path to found config file
    :raises: InvalidConfig if config file is not found or cannot
             be loaded.
    """
    if conf:
        if os.path.isfile(conf):
            return conf
        else:
            raise InvalidConfig('Specified config file not found at %s' % conf)

    root = os.path.abspath(os.path.join(os.path.realpath(__file__), '../..'))
    env_conf = os.getenv('WEEBL_ROOT', root)
    env_conf = (env_conf and
                os.path.join(env_conf, 'etc', 'weebl', 'weebl.conf'))
    if env_conf and os.path.isfile(env_conf):
        return env_conf

    raise InvalidConfig('Could not find config file')


def _load_config(conf_file):
    config = configparser.RawConfigParser()
    loaded = config.read(conf_file)
    if not loaded:
        msg = 'Config not loaded: %s' % conf_file
        raise InvalidConfig(msg)
    return config


def get_config(conf=None):
    if _config and not conf:
        return _config[0]

    conf_file = find_config(conf)
    config = _load_config(conf_file)
    _config.append(config)
    return config


def get_mode(mode=None):
    if not mode:
        # TODO: Look in etc for the mode file and assign the contents of that
        # (i.e. 'DEFAULT', or 'TESTING') to mode, otherwise mode = 'DEFAULT'
        mode = 'DEFAULT'
    return mode
