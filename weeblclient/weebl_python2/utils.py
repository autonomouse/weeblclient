import os
import yaml
import random
import string
import logging
import subprocess
from fnmatch import fnmatch
from datetime import datetime
from collections import namedtuple
from copy import deepcopy

_config = []
_loggers = {}

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'


def _get_logger(name, level='DEBUG', logfile=None):
    _logger = logging.getLogger(name)
    _logger.propagate = False

    if level == 'DEBUG':
        lvl = logging.DEBUG
    elif level == 'INFO':
        lvl = logging.INFO

    _logger.setLevel(lvl)

    if logfile:
        f = logging.FileHandler(logfile)
        f.setLevel(lvl)
        f.setFormatter(logging.Formatter(LOG_FORMAT))
        print("Logging to {}".format(logfile))
        _logger.addHandler(f)
    else:
        c = logging.StreamHandler()
        c.setFormatter(logging.Formatter(LOG_FORMAT))
        _logger.addHandler(c)

    return _logger


def get_logger(name='weebl_client', logfile=None):
    if _loggers.get(name):
        # Use the existing logger.
        return _loggers.get(name)

    if os.getenv('WEEBL_CLIENT_DEBUG'):
        level = 'DEBUG'
    else:
        level = 'INFO'

    logger = _get_logger(name=name, level=level, logfile=logfile)
    _loggers[name] = logger
    return logger


def convert_timestamp_to_dt_obj(timestamp):
    timestamp_in_ms = timestamp / 1000
    return datetime.fromtimestamp(timestamp_in_ms)


def convert_timestamp_to_string(timestamp, ts_format='%a %d %b %Y %H:%M:%S'):
    if type(timestamp) is datetime:
        return timestamp.strftime(ts_format)
    dt_obj = convert_timestamp_to_dt_obj(timestamp)
    return dt_obj.strftime(ts_format)


def generate_random_string(n=10, uppercase=False):
    ascii = string.ascii_uppercase if uppercase else string.ascii_lowercase
    return "".join(random.choice(ascii) for i in range(n))


def get_internal_url_of_this_machine():
    return subprocess.check_output(["hostname", "-I"]).split()[0]


def merge_dict(onto, source):
    target = deepcopy(onto)
    for (key, value) in source.items():
        if (key in target and isinstance(target[key], dict) and
                isinstance(value, dict)):
            target[key] = merge_dict(target[key], value)
        elif (key in target and isinstance(target[key], list) and
              isinstance(value, list)):
            target[key].extend(value)
        else:
            target[key] = value
    return target


def munge_bug_info_data(known_bug_regexes):
    """Get the data and put it into the format doberman is expecting (the
    same as test-catalog's get_bug_info method).
    """
    bugs_dict = {}
    for known_bug_regex in known_bug_regexes:
        known_bug_regex_uuid = known_bug_regex['uuid']
        known_bug_regex_regex = known_bug_regex['regex']
        try:
            lp_bug = known_bug_regex['bug']['bugtrackerbug']['bug_number']
        except TypeError:
            continue
        except KeyError:
            continue
        for glob in known_bug_regex['targetfileglobs']:
            if not isinstance(glob, dict):
                continue
            target_file_glob = glob.get('glob_pattern')
            if target_file_glob is None:
                continue
            job_names = [jobtype.get('name')
                         for jobtype in glob.get('jobtypes')]
            for job_name in job_names:
                job_entry = {target_file_glob: {
                    'regexp': [known_bug_regex_regex],
                    'uuids': [known_bug_regex_uuid]}
                }
                # top level regex_uuid is wrong, but doberman expects it, so...
                bug_dict_partial = {
                    lp_bug: {job_name: [job_entry],
                             'regex_uuid': known_bug_regex_uuid}}
                bugs_dict = merge_dict(bugs_dict, bug_dict_partial)

    return {'bugs': bugs_dict}


def generate_bug_entries(bugs_dict, include_generics):
    Entry = namedtuple('Entry', [
        'lp_bug_no', 'job', 'targetfileglob', 'regex', 'summary'])
    entry_list = []
    for lp_bug_no, entry in bugs_dict['bugs'].items():
        if not include_generics:
            if lp_bug_no == 'GenericBug_Ignore':
                continue
        summary = entry.get('description')
        try:
            entry.pop('description')
        except KeyError:
            pass
        try:
            entry.pop('category')
        except KeyError:
            pass
        for job, job_entry in entry.items():
            for item in job_entry:
                for targetfileglob, value in item.iteritems():
                    regex_list = value['regexp']
                    for regex in regex_list:
                        if summary in [None, '']:
                            summary = regex
                        entry = Entry(lp_bug_no, job, targetfileglob,
                                      regex, summary)
                        entry_list.append(entry)
    return entry_list


def mkdir(directory):
    """ Make a directory, check and throw an error if failed. """
    if directory in ['', None, '.']:
        return
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError:
            if not os.path.isdir(directory):
                raise


def load_yaml(file_location):
    with open(file_location, "r") as f:
        return yaml.load(f)


def write_output_yaml(output, path_to_file):
    mkdir(os.path.dirname(path_to_file))
    stream = yaml.safe_dump(output, default_flow_style=False)
    with open(path_to_file, 'w') as outfile:
        outfile.write(stream)
