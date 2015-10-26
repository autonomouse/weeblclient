import os
import random
import string
import logging
import subprocess
from datetime import datetime

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


def munge_bug_info_data(target_file_globs, known_bug_regexes, wbugs):
    """Get the data and put it into the format doberman is expecting (the
    same as test-catalog's get_bug_info method).
    """
    regex_dict, tfile_list = build_dict_of_linked_items(
        target_file_globs, known_bug_regexes, wbugs)
    return build_bug_info_dict(regex_dict, tfile_list, wbugs)


def build_dict_of_linked_items(target_file_globs, known_bug_regexes, wbugs):
    """Builds a dictionary with each regex as the key and associates to that
    regex a tuple containing the target_file_glob, job_type and launchpad bug
    (bugtrackerbug).
    """
    regex_dict = {}
    tfile_list = []
    for weebl_bug in wbugs:
        lp_bug = weebl_bug['bugtrackerbug']['bug_number']
        for targetfileglob in target_file_globs:
            tfile = targetfileglob['glob_pattern']
            if tfile not in tfile_list:
                tfile_list.append(tfile)
            jobs = targetfileglob.get('jobtypes', [])
            if jobs == []:
                continue
            for job in jobs:
                job_type = job[16:-1]
                for kbr_resource in weebl_bug['knownbugregex']:
                    for knownbugregex in known_bug_regexes:
                        if kbr_resource == knownbugregex['resource_uri']:
                            filesaffected = knownbugregex.get(
                                'targetfileglobs')
                            matching_tfiles = [file for file in filesaffected
                                               if tfile in file]
                            if matching_tfiles == []:
                                continue
                            regex = knownbugregex['regex']
                            if regex not in regex_dict:
                                regex_dict[regex] = []
                            regex_dict[regex].append((tfile, job_type, lp_bug))
    return regex_dict, tfile_list


def build_bug_info_dict(regex_dict, tfile_list, wbugs):
    """Takes the regex_dict generated by the build_dict_of_linked_items method
    and builds a dictionary in the format doberman is expecting.
    """
    bug_info = {'bugs': {}}
    for weebl_bug in wbugs:
        lp_bug = weebl_bug['bugtrackerbug']['bug_number']
        for tfile in tfile_list:
            for regex, linked_info_list in regex_dict.items():
                for linked_info in linked_info_list:
                    if lp_bug != linked_info[2]:
                        continue
                    if tfile != linked_info[0]:
                        continue
                    job_type = linked_info[1]
                    if lp_bug not in bug_info['bugs']:
                        bug_info['bugs'][lp_bug] = {}
                    if job_type not in bug_info['bugs'][lp_bug]:
                        bug_info['bugs'][lp_bug][job_type] = []

                    subdict = bug_info['bugs'][lp_bug][job_type]
                    if subdict == []:
                        subdict.append({})
                        idx = 0
                    else:
                        idx = [idx for idx, xxx in enumerate(bug_info['bugs']
                               [lp_bug][job_type]) if tfile in xxx][0]
                    if tfile not in subdict[idx]:
                        subdict[idx][tfile] = {'regexp': []}
                    subdict[idx][tfile]['regexp'].append(regex)
    return bug_info
