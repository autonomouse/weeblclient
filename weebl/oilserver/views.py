import os
import yaml
import operator
import json
import utils
from datetime import datetime
from django.shortcuts import render
from exceptions import AbsentYamlError
from collections import namedtuple

cfg = utils.get_config()
MODE = utils.get_mode()
bug_ranking_files = json.loads(cfg.get(MODE, 'bug_ranking_files')
                               .replace("'", "\""))
root_data_directory = cfg.get(MODE, 'data_dir')


def load_from_yaml_file(file_location):
    """Return data from yaml file."""

    if not os.path.exists(file_location):
        raise AbsentYamlError("{} missing".format(file_location))

    with open(file_location, 'r') as oil_file:
        return yaml.load(oil_file)

def get_current_oil_state(data_location, env):
    """Load up report status"""
    env.oil_state = 'normal'
    env.oil_situation = []
    
    status = load_from_yaml_file(os.path.join(data_location, 'report_status'))
    
    # Work out how long it's been since it last checked in:
    timestamp = datetime.strptime(status['last_time_jenkins_reported'], 
                                  '%Y-%m-%d %H:%M:%S')                                                 
    time_difference = datetime.utcnow() - timestamp
    warning_th = cfg.get(MODE, 'check_in_warning_threshold')
    critical_th = cfg.get(MODE, 'check_in_critical_threshold')
    if time_difference.seconds > float(critical_th):
        env.oil_state = 'critical'
        msg = "It has been over {} seconds since jenkins last checked in."
        env.oil_situation.append(msg.format(critical_th))
    elif time_difference.seconds > float(warning_th):
        env.oil_state = 'warning'
        msg = "It has been over {} seconds since jenkins last checked in."
        env.oil_situation.append(msg.format(warning_th))
    
    # Determine if there are any dead nodes:
    body_count = len(status['dead_nodes'])
    if body_count > 0:
        env.oil_state = 'warning'
        msg = "{} nodes are reported as dead.".format(body_count)
        env.oil_situation.append(msg)
    
    # Determine if there are too few builds in the queue:
    builds_in_q = len(status['start_builds_queue'])
    build_q_th = cfg.get(MODE, 'low_build_queue_threshold')
    if builds_in_q < int(build_q_th):
        env.oil_state = 'warning'
        msg = "There are only {} pipeline_start builds currently in the queue."
        env.oil_situation.append(msg.format(build_q_th))        
    
    # Determine if there are any builds that are hanging:
    # TODO - not yet implemented on jenkins
    
    # Determine if the Queue Daemon has stopped:
    # TODO - not yet implemented on jenkins    
    
    return env
    
def get_timestamp(data_location, tframe):
    """Load up timestamp that oil-stats was run."""
    
    tframe.timestamp = \
        load_from_yaml_file(os.path.join(data_location, 'timestamp'))    
    return tframe
    
def get_oil_stats(data_location, tframe):
    """Load up oilstats"""
    
    oil_stats = \
        load_from_yaml_file(os.path.join(data_location, 'oil-stats.yaml'))
    if not oil_stats:
        return
    tframe.success_rate = str(round(oil_stats['overall']['success rate'], 2))
    tframe.job_success_rates = {}
    for jobname, yaml_file in bug_ranking_files.items():
        tframe.job_success_rates[jobname] = \
            str(round(oil_stats['jobs'][jobname]['success rate'], 2))
    return tframe
    
def get_bug_ranking_data(data_location, tframe, limit=None):
    """Load up bug_ranking data."""
    tframe.rankings = {}
    for jobname, yaml_file in bug_ranking_files.items():
        job_ranking = load_from_yaml_file(os.path.join(data_location, 
                                                       yaml_file))
        job_ranking = dict(job_ranking) if job_ranking else {}
        
        bugs = [ranking for ranking in job_ranking.items()]
        
        # Sort bugs by number of hits:
        sorted_bugs = sorted(bugs, key=operator.itemgetter(1), reverse=True)
        tframe.rankings[jobname] = job_ranking
        sorted_bugs = sorted_bugs[:limit] if limit != None else sorted_bugs
        tframe.rankings[jobname] = sorted_bugs
    return tframe
        

def acquire_data(environment, root_data_directory, time_range='daily', 
                 limit=None):
    """Get all relevant data."""
    data = namedtuple('data','')
    data.env = {environment: namedtuple('env','')}
    data.env[environment].name = environment
    data.env[environment].tframe = namedtuple('tframe','')

    env_data_location = os.path.join(root_data_directory, environment)
    time_range_data_location = os.path.join(env_data_location, time_range)
        
    data.title = 'main_page'
    data.env[environment] = get_current_oil_state(env_data_location, 
                                                   data.env[environment])    
    tframe = data.env[environment].tframe
    tframe = get_timestamp(time_range_data_location, tframe)
    tframe = get_oil_stats(time_range_data_location, tframe)
    tframe = get_bug_ranking_data(time_range_data_location, tframe, limit)
    return convert_named_tuple_to_dict(data)

def convert_named_tuple_to_dict(data):
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
                        value2 = convert_named_tuple_to_dict(value2)
                    out[key][key2] = value2
            else:
                out[key] = value
    return out
    

def main_page(request):
    for env_folder in os.listdir(root_data_directory):
        environment = os.path.basename(env_folder)
        # Show daily results and limit the number of bugs to the top ten:
        data = acquire_data(environment, root_data_directory, 
                            time_range='daily', limit=10) 
    return render(request, 'main_page.html', data)


def job_specific_bugs_list(request, job):
    data = {'title': 'job_specific_bugs_list',
            'job': job, }
    for env_folder, parent, files in os.walk(root_data_directory):
        if env_folder == root_data_directory:
            continue
        environment = os.path.basename(env_folder)
        data = load_data(environment, root_data_directory, data)
    return render(request, 'job_specific_bugs_list.html', data)

