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
js_down_th = json.loads(cfg.get(MODE, 'job_specific_down_th')
                                .replace("'", "\""))
js_unstable_th = json.loads(cfg.get(MODE, 'job_specific_unstable_th')
                                    .replace("'", "\""))


def load_from_yaml_file(file_location):
    """Return data from yaml file."""

    if not os.path.exists(file_location):
        raise AbsentYamlError("{} missing".format(file_location))

    with open(file_location, 'r') as oil_file:
        return yaml.load(oil_file)
  
def get_current_oil_state(data_location, env):
    """Load up report status"""
    env.oil_state = 'up'
    env.oil_state_colour = cfg.get(MODE, '{}_colour'.format(env.oil_state))
    env.oil_situation = []

    status = load_from_yaml_file(os.path.join(data_location, 'report_status'))

    # Work out how long it's been since it last checked in:
    timestamp = datetime.strptime(status['last_time_jenkins_reported'],
                                  '%Y-%m-%d %H:%M:%S')
    time_difference = datetime.utcnow() - timestamp
    unstable_th = cfg.get(MODE, 'check_in_unstable_threshold')
    down_th = cfg.get(MODE, 'check_in_down_threshold')

    if time_difference.seconds > float(down_th):
        msg = "It has been over {} seconds since jenkins last checked in."
        set_oil_state(env, 'down', msg.format(unstable_th))
    elif time_difference.seconds > float(unstable_th):
        msg = "It has been over {} seconds since jenkins last checked in."
        set_oil_state(env, 'unstable', msg.format(unstable_th))

    # Determine if there are any dead nodes:
    body_count = len(status['dead_nodes'])
    if body_count > 0:
        msg = "The following {} nodes are reported as dead: {}"
        msg = msg.format(body_count, status['dead_nodes'])
        set_oil_state(env, 'unstable', msg)

    # Determine if there are too few builds in the queue:
    builds_in_q = len(status['start_builds_queue'])
    build_q_th = cfg.get(MODE, 'low_build_queue_threshold')
    if builds_in_q < int(build_q_th):
        msg = "There are only {} pipeline_start builds currently in the queue."
        set_oil_state(env, 'unstable', msg.format(build_q_th))

    # Determine if there are any builds that are hanging:
    # TODO - not yet implemented on jenkins

    # Determine if the Queue Daemon has stopped:
    # TODO - not yet implemented on jenkins

    return env

def set_oil_state(env, new_state, msg):  
    # Set state:      
    if env.oil_state != 'down':
        env.oil_state = new_state

    # Set colour:    
    env.oil_state_colour = cfg.get(MODE, '{}_colour'.format(env.oil_state))

    # Set message:  
    if msg != '':
        env.oil_situation.append(msg)
    return env.oil_state

def get_timestamp(data_location, tframe):
    """Load up timestamp that oil-stats was run."""

    tframe.timestamp = \
        load_from_yaml_file(os.path.join(data_location, 'timestamp'))
    return tframe

def get_oil_stats(data_location, tframe):
    """Load up oilstats"""

    try:
        oil_stats = \
            load_from_yaml_file(os.path.join(data_location, 'oil-stats.yaml'))
    except AbsentYamlError:
        oil_stats = {'jobs': {'pipeline_deploy': {'success rate': '?'},
                              'pipeline_prepare': {'success rate': '?'},
                              'test_tempest_smoke': {'success rate': '?',}},
                     'overall': {'success rate': '?',
                                 'tempest builds': '?',
                                 'total jobs': '?'}}
    if not oil_stats:
        return
    SRate = oil_stats['overall']['success rate']
    overall = round(SRate, 2) if SRate != '?' else '?'
    if overall == '?' or overall < float(cfg.get(MODE, 'overall_down_th')):
        tframe.overall_colour = cfg.get(MODE, 'down_colour')
    elif overall < float(cfg.get(MODE, 'overall_unstable_th')):
        tframe.overall_colour = cfg.get(MODE, 'unstable_colour')
    else:
        tframe.overall_colour = cfg.get(MODE, 'up_colour')
    tframe.success_rate = str(overall)
    tframe.job_success_rates = {}
    tframe.job_success_rate_col = {}
    for jobname, yaml_file in bug_ranking_files.items():
        OvAll = oil_stats['jobs'][jobname]['success rate']
        success = round(OvAll, 2) if OvAll != '?' else '?'
        if success == '?' or success < float(js_down_th[jobname]):
            tframe.job_success_rate_col[jobname] = cfg.get(MODE, 'down_colour')
        elif success < float(js_unstable_th[jobname]):
            tframe.job_success_rate_col[jobname] = \
                cfg.get(MODE, 'unstable_colour')
        else:
            tframe.job_success_rate_col[jobname] = cfg.get(MODE, 'up_colour')
        tframe.job_success_rates[jobname] = str(success)

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

def merge_with_launchpad_data(data_location, tframe, database):
    lp_data = get_launchpad_data(data_location)
    cats = {}
    
    for job, job_ranking in tframe.rankings.items():
        for idx, (bug, hits) in enumerate(job_ranking):
            bug_data = lp_data['tasks'].get(bug)
            if bug_data:
                bug_data = bug_data[0]                
                lp_link = \
                    os.path.join(cfg.get(MODE, 'launchpad_bugs_url'), bug)
                assignee = bug_data['assignee']
                age_days = bug_data['bug']['age_days']
                date_assigned = bug_data['date_assigned']
                title = bug_data['bug']['title']
                importance = bug_data['importance']
                status = bug_data['status']        
                all_tags = bug_data['bug']['tags']               
            else:
                lp_link = None
                assignee = ''
                age_days = ''
                date_assigned = ''
                title = ''
                importance = ''
                status = ''     
                all_tags = ''  
            cats = link_tags_with_hi_lvl_categories(cats, database, tframe, 
                                                    job, bug)
            tframe.rankings[job][idx] = (bug, lp_link, hits, lp_link, title,
                                         assignee, age_days, cats, importance, 
                                         status, date_assigned, all_tags)
    breakdown = {}
    for category in cats:
        breakdown[category] = len(cats[category])
    # Sort bugs by number of eachcategory:
    #breakdown = sorted(breakdown, key=operator.itemgetter(1), reverse=True)
    return (tframe, cats, breakdown)

def get_launchpad_data(data_location):
    file_location = os.path.join(data_location, 'OIL.json')
    if not os.path.exists(file_location):
        raise AbsentYamlError("{} missing".format(file_location))

    with open(file_location, 'r') as lp_file:
        return yaml.load(lp_file)

def link_tags_with_hi_lvl_categories(categories, database, tframe, job, 
                                     bug_id):
    for bug in tframe.rankings[job]:
        if bug[0] == bug_id:
            db_bug = database['bugs'].get(bug_id)
            category = db_bug.get('category') if db_bug else ['Unknown']
            if category in [[], None, 'None']:
                category = ['Unknown']
            for cat in category:
                if cat not in categories:
                     categories[cat] = []
                categories[cat].append(bug_id)
    return categories

def get_common_data(environments, root_data_directory, time_range='daily',
                    limit=None):
    """Get all relevant data."""
    # Load up data from files:
    with open(os.path.join(root_data_directory, 'database.yaml'), 'r') as db:
        database = yaml.load(db)
        
    data = namedtuple('data','')
    data.env = {}
    for environment in environments:
        data.env[environment] = namedtuple('env','')
        data.env[environment].name = environment
        data.env[environment].tframe = namedtuple('tframe','')

        env_data_location = os.path.join(root_data_directory, environment)
        time_range_data_location = os.path.join(env_data_location, time_range)

        data.title = 'main_page'
        try:
            data.env[environment] = \
                get_current_oil_state(env_data_location, data.env[environment])
        except AbsentYamlError:
            data.env[environment].oil_state = 'down'
            data.env[environment].oil_state_colour = \
                cfg.get(MODE,
                        '{}_colour'.format(data.env[environment].oil_state))
            data.env[environment].oil_situation = \
                ["No report_status file found"]
        tframe = data.env[environment].tframe
        tframe = get_timestamp(time_range_data_location, tframe)
        tframe = get_oil_stats(time_range_data_location, tframe)
        tframe = get_bug_ranking_data(time_range_data_location, tframe, limit)
        tframe, data.categories, data.breakdown = \
            merge_with_launchpad_data(root_data_directory, tframe, database)
    return data

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

def main_page(request, time_range='daily'):
    environments = [env for env in os.listdir(root_data_directory)
                    if os.path.isdir(os.path.join(root_data_directory, env))]
    # Show (daily?) results and limit the number of bugs to the top ten:
    data = get_common_data(environments, root_data_directory, time_range, 10)
    data.time_range = time_range
    return render(request, 'main_page.html', conv_to_dict(data))

def weekly_main_page(request, time_range='weekly'):
    return main_page(request, time_range)

def job_specific_bugs_list(request, job, time_range='daily',
                           specific_env='all'):
    # TODO: environments should be an argument, really, defaulting to all
    if specific_env == 'all':
        environments = [env for env in os.listdir(root_data_directory) if
                        os.path.isdir(os.path.join(root_data_directory, env))]
    else:
        environments = [specific_env]
    data = get_common_data(environments, root_data_directory, time_range)
    data.job = job
    data.time_range = time_range
    return render(request, 'job_specific_bugs_list.html', conv_to_dict(data))
