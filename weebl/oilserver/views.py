import os
import yaml
import operator
from django.shortcuts import render


# TODO: This shouldn't be hard-coded here:
files = {'pipeline_deploy': 'bug_ranking_pipeline_deploy.yml',
         'pipeline_prepare': 'bug_ranking_pipeline_prepare.yml',
         'test_tempest_smoke': 'bug_ranking_test_tempest_smoke.yml'}
root_data_directory = "./data"


def get_yaml(file_location):
    """ Return data from yaml file. """

    if not os.path.exists(file_location):
        return

    with open(file_location, 'r') as oil_file:
        return yaml.load(oil_file)


def oil_status(environment):
    """ Request current oil status. """
    # TODO: is OIL up/down?
    status = "DOWN (not really - this isn't implemented yet)"
    return status


def load_data(environment, root_data_directory, data):
    """ Load up oilstats, timestamp and bug_ranking data. """

    data_location = '{}/{}'.format(root_data_directory, environment)

    if 'environments' not in data:
        data['environments'] = {}

    data['environments'][environment] = {'name': environment, 'rankings': {}}

    # Get the date/time oil-stats was run:
    timestamp = get_yaml(os.path.join(data_location, 'timestamp'))
    data['environments'][environment]['timestamp'] = timestamp

    # Request current oil status
    data['environments'][environment]['oil_state'] = oil_status(environment)

    # Get oil-stats data:
    oil_stats = get_yaml(os.path.join(data_location, 'oil-stats.yml'))
    if oil_stats:
        data['environments'][environment]['success_rate'] = \
            str(round(oil_stats['overall']['success rate'], 2)) + "%"
    else:
        data['environments'][environment]['success_rate'] = "?"

    # Get pipelines and associated build numbers file:
    # paabn = get_yaml(os.path.join(data_location,
    #                  'pipelines_and_associated_build_numbers.yml'))

    # Get data:
    for jobname, yaml_file in files.items():
        job_ranking = get_yaml(os.path.join(data_location, yaml_file))
        job_ranking = dict(job_ranking) if job_ranking else {}
        if oil_stats:
            data['environments'][environment][jobname] = \
                str(round(oil_stats['jobs'][jobname]['success rate'], 2)) + "%"
        else:
            data['environments'][environment][jobname] = "?"
        data['environments'][environment]['rankings'][jobname] = {}
        for key, hits in job_ranking.items():
            data['environments'][environment]['rankings'][jobname][key] = hits

        bugs = [ranking for count, ranking in enumerate(job_ranking.items())]
        sorted_bugs = sorted(bugs, key=operator.itemgetter(1), reverse=True)
        data['environments'][environment]['rankings'][jobname] = sorted_bugs
    return data


def load_top_ten_data(environment, root_data_directory, data, mock_data=None):
    """ Restrict data loaded up to only the top ten by number of hits. """
    if not mock_data:
        data = load_data(environment, root_data_directory, data)
    else:
        data = mock_data  # used for unit testing
    for env, values in data['environments'].items():
        if 'rankings' not in values:
            continue
        for job, rankings in values['rankings'].items():
            top_ten = [ranking for count, ranking in
                       enumerate(rankings) if count < 10]
            sorted_top10 = sorted(top_ten, key=operator.itemgetter(1),
                                  reverse=True)
            data['environments'][env]['rankings'][job] = sorted_top10
    return data


def main_page(request):
    data = {'title': 'main_page'}
    for env_folder, parent, files in os.walk(root_data_directory):
        if env_folder == root_data_directory:
            continue
        environment = env_folder.split('/')[-1]
        data = load_top_ten_data(environment, root_data_directory, data)
    return render(request, 'main_page.html', data)


def job_specific_bugs_list(request, job):
    data = {'title': 'job_specific_bugs_list',
            'job': job, }
    for env_folder, parent, files in os.walk(root_data_directory):
        if env_folder == root_data_directory:
            continue
        environment = env_folder.split('/')[-1]
        data = load_data(environment, root_data_directory, data)
    return render(request, 'job_specific_bugs_list.html', data)
