import re
import pytz
from datetime import datetime
from dateutil import parser
from django.utils import timezone
from uuid import uuid4

def conv_to_dict(data):
    """Converts from those multi-level namedtuples that seemed such a good idea
    at the time back into a dictionary.

    Example data structure (for daily data on production):

    data['title']
        - The title of the page

    data['env']['name']
        - The name of this environment (in this example: 'production')

    data['env']['production']['oil_state']
        - The current status of the 'production' OIL environment

    data['env']['production']['oil_situation']
        - An explanation for the current status of the OIL environment

    data['env']['production']['tframe']['success_rate']
        - The overall success rate of from daily oil-stats run on production

    data['env']['production']['tframe']['timestamp']
        - The time when the daily oil-stats were run on production data

    data['env']['production']['tframe']['job_success_rates']
        - A dict of each job and it's individual success rate

    data['env']['production']['tframe']['rankings']['pipeline_deploy']
        - A list of tuples showing the bugs hit and count for the
          pipeline_deploy job (in this case)
    """
    out = {}
    for key, value in vars(data).items():
        if not key.startswith('_'):
            out[key] = {}
            if type(value) == dict:
                for key2, value2 in value.items():
                    if type(value2) == type:
                        value2 = conv_to_dict(value2)
                    out[key][key2] = value2
            else:
                out[key] = value
    return out

def time_now():
    return timezone.now()

def time_since(timestamp):
    if timestamp is None:
        return

    if type(timestamp) is not datetime:
        timestamp_dt = parser.parse(timestamp)
    else:
        timestamp_dt = timestamp.replace(tzinfo=None)
    return timezone.now() - pytz.utc.localize(timestamp_dt)

def uuid_check(uuid):
    uuid_pattern = "^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}"
    uuid_pattern += "-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z"
    regex = re.compile(uuid_pattern, re.I)
    match = regex.match(uuid)
    return bool(match)

def generate_uuid():
    return str(uuid4())
