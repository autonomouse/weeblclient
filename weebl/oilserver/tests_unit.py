#! /usr/bin/env python3

from oilserver.views import (main_page, job_specific_bugs_list)
from django.http import HttpRequest
from common_test_methods import WeeblTestCase



'''
import views
change views.root_data_directory to a mock data folder
generate new timestamp files, etc 
test individual methods (e.g. get_current_oil_state) work


'''

class DevSmokeTests(WeeblTestCase):

    def test_main_page(self):
        request = HttpRequest()
        response = main_page(request)
        self.assertIn(b'main_page', response.content)
'''
    def test_job_specific_bugs_list(self):
        request = HttpRequest()
        job = 'pipeline_deploy'
        response = job_specific_bugs_list(request, job)
        self.assertIn(b'job_specific_bugs_list', response.content)
        self.assertIn(b'pipeline_deploy', response.content)
'''
''' 
    unit tests set up mock data folder with mock data and different timestamps 
    etc to see if it shows up correctly or not. Also use this for my talk.
'''




class UnitTests(WeeblTestCase):

    def test_load_from_yaml_file(self):
        
        import pdb;pdb.set_trace()
        
        a_dictionary = {'a': 1, 'b': 2, 'c': 3}
        self.create_temporary_yaml_file(a_dictionary)     
"""    
        
        self.create_mock_data('test_data', 'data')
        
        
        file_location = 'weebl/oilserver/mock_data'
        #with open()
        
        # create a yaml file
        
        oil_yaml = load_from_yaml_file(file_location)
"""  
"""  
get_current_oil_state(data_location, env):

    return env

def set_oil_state(env, new_state, msg)

    return env.oil_state

def get_timestamp(data_location, tframe)

    return tframe

def get_oil_stats(data_location, tframe)

    return tframe

def get_bug_ranking_data(data_location, tframe, limit=None)

    return tframe

def merge_with_launchpad_data(data_location, tframe)

    return (tframe, cats, breakdown)

def get_launchpad_data(data_location)

        return yaml.load(lp_file)

def link_tags_with_hi_lvl_categories(categories, all_tags, tframe, job, 
                                     bug_id, bug_cats):
    return (categories, bug_cats)

def get_common_data(environments, root_data_directory, time_range='daily',
                    limit=None):

    return data

def conv_to_dict(data):

    return out

def main_page(request, time_range='daily'):
    environments = [env for env in os.listdir(root_data_directory)

    return render(request, 'main_page.html', conv_to_dict(data))

def weekly_main_page(request, time_range='weekly'):
    return main_page(request, time_range)

def job_specific_bugs_list(request, job, time_range='daily',
                           specific_env='all'):

    return render(request, 'job_specific_bugs_list.html', conv_to_dict(data))
"""
