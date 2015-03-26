import sys
import os
import yaml
from django.shortcuts import render


def get_yaml(file_location):
    """ Return data from yaml file. """

    if not os.path.exists(file_location):
        return

    with open(file_location, 'r') as oil_file:
        return yaml.load(oil_file)
        
def request_current_oil_status(environment):
    # TODO
    pass
    
def load_data(environment, data):
    """ Load up oilstats, timestamp and bug_ranking data. """
    
    if 'environments' not in data:
        data['environments'] = {}
    data['environments'][environment] = {'name': environment}
    
    data_location = './data/{}'.format(environment)        

    oil_stats = get_yaml(os.path.join(data_location, 'oil-stats.yml'))
    deploy_ranking = get_yaml(os.path.join(data_location,
                              'bug_ranking_pipeline_deploy.yml'))
    prepare_ranking = get_yaml(os.path.join(data_location,
                               'bug_ranking_pipeline_prepare.yml'))
    tempest_ranking = get_yaml(os.path.join(data_location,
                               'bug_ranking_test_tempest_smoke.yml'))
    paabn = get_yaml(os.path.join(data_location,
                     'pipelines_and_associated_build_numbers.yml'))
    timestamp = get_yaml(os.path.join(data_location, 'timestamp'))
    
    # Put relevant data into data:
    data['environments'][environment]['timestamp'] = timestamp
    data['environments'][environment]['oil_state'] = "DOWN (not really - this isn't implemented yet)"

    if oil_stats:
        data['environments'][environment]['success_rate'] = oil_stats['overall']['success rate']
        data['environments'][environment]['deploy'] = oil_stats['jobs']['pipeline_deploy']['success rate']
        data['environments'][environment]['prepare'] = oil_stats['jobs']['pipeline_prepare']['success rate']
        data['environments'][environment]['tempest'] = \
            oil_stats['jobs']['test_tempest_smoke']['success rate']

        deploy_ranking = dict(deploy_ranking) if deploy_ranking else {}
        prepare_ranking = dict(prepare_ranking) if prepare_ranking else {}
        tempest_ranking = dict(tempest_ranking) if tempest_ranking else {}
        
        deploy_paabn_ranking = {}
        for key, hits in deploy_ranking.items():
            deploy_paabn_ranking[key] = paabn.get(key, {})
            deploy_paabn_ranking[key]['hits'] = hits    
        
        prepare_paabn_ranking = {}
        for key, hits in prepare_ranking.items():
            prepare_paabn_ranking[key] = paabn.get(key, {})
            prepare_paabn_ranking[key]['hits'] = hits
            
        tempest_paabn_ranking = {}
        for key, hits in tempest_ranking.items():
            tempest_paabn_ranking[key] = paabn.get(key, {})
            tempest_paabn_ranking[key]['hits'] = hits
        
        data['environments'][environment]['rankings'] = {}
        data['environments'][environment]['rankings']['deploy'] = deploy_paabn_ranking
        data['environments'][environment]['rankings']['prepare'] = prepare_paabn_ranking
        data['environments'][environment]['rankings']['tempest'] = tempest_paabn_ranking
    
    return data

def main_page(request):
    
    data = {'title': 'main_page'}
    data = load_data('staging', data)
    data = load_data('prodstack', data)
    return render(request, 'main_page.html', data)

def job_specific_bugs_list(request, job):
    data = {'title': 'job_specific_bugs_list',
            'job': job,}
    return render(request, 'job_specific_bugs_list.html', data)

