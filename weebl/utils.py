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

    env_conf = os.getenv('WEEBL_ROOT', None)
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
