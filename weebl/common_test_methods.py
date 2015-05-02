import os
import tempfile
import yaml
import shutil
from random import random, randint
from django.test import TestCase
from datetime import datetime
from dateutil.parser import parse
from datetime import datetime


class WeeblTestCase(TestCase):
    # Helper methods:
    def mock_batch_oil_stats_data(self):
        pass

    def makedirs(self, path):
        try:
            os.makedirs(path)
        except OSError:
            pass

    def write_to_file(self, path_to_file, text):
        with open(path_to_file, 'w') as f:
            f.write(text)

    def get_timestamp(self, when):
        if when == 'now':
            timestamp = datetime.now()
        else:
            timestamp = parse(when)
        return timestamp.strftime('%F_%T')

    def create_temporary_file(self, where, name, content):
        file_loc = os.path.join(where, name)
        with open(file_loc, 'w') as temp:
            temp.write(content)
            temp.flush()
        return temp.name

    def create_temporary_yaml_file(self, name, dictionary, where=None):
        if where is None:
            jnk, file_loc = tempfile.mkstemp()
            where = os.path.dirname(file_loc)
            new_name = os.path.join(where, name)
            shutil.move(file_loc, new_name)
        content = yaml.dump(dictionary)
        return self.create_temporary_file(where, name, content)

    def create_timestamp_file(self, where, when):
        name = 'timestamp'
        content = self.get_timestamp(when)
        return self.create_temporary_file(where, name, content)

    def create_report_status(self, where, threshold=10800):
        content = {"dead_nodes": ['master'], 
                   "build_hanging_time_threshold": threshold, 
                   "last_time_jenkins_reported": "2000-01-01 00:00:00", 
                   "start_builds_queue": [1, 2, 3, 4, 5]}
        return self.create_temporary_yaml_file('report_status', content, where)
        
    def create_oil_stats_yaml(self, where):
        results = {'jobs': {'overall': {}}}

        # write deploy job
        dply_bld_obj = round(random() * 100)
        dply_cmp_bld = round(random() * 100)
        dply_st_date = ''  # datetime.random(random())
        dply_st_job = round(random() * 100)
        dply_end_date =  ''  # datetime.random(random())
        dply_end_job = round(random() * 100)
        dply_fails = round(random() * 100)
        dply_passes = round(random() * 100)
        dply_still_run = round(random() * 100)
        dply_success = round(random() * 100)

        results['jobs']['pipeline_deploy'] = \
            {'build objects': dply_bld_obj,
             'completed builds': dply_cmp_bld,
             'start date': dply_st_date,
             'start job': dply_st_job,
             'end date': dply_end_date,
             'end job': dply_end_job,
             'fails': dply_fails,
             'passes': dply_passes,
             'still running': dply_still_run,
             'success rate': dply_success}

        # write tempest job
        tmpst_bld_obj = round(random() * 100)
        tmpst_cmp_bld = round(random() * 100)
        tmpst_st_date =  ''  # datetime.random(random())
        tmpst_st_job = round(random() * 100)
        tmpst_end_date =  ''  # datetime.random(random())
        tmpst_end_job = round(random() * 100)
        tmpst_gd_blds = round(random() * 100)
        tmpst_skip = round(random() * 100)
        tmpst_total = round(random() * 100) + tmpst_skip
        tmpst_ttl_wo_skip = tmpst_total - tmpst_skip

        results['jobs']['test_tempest_smoke'] = \
            {'build objects': tmpst_bld_obj,
             'completed builds': tmpst_cmp_bld,
             'start date': tmpst_st_date,
             'start job': tmpst_st_job,
             'end date': tmpst_end_date,
             'end job': tmpst_end_job,
             'good builds': tmpst_gd_blds,
             'skipped': tmpst_skip,
             'total': tmpst_total,
             'total without skipped': tmpst_ttl_wo_skip}

        # write overall
        tt = random()
        td = random()
        overall = (tt / td) * 100.0
        results['jobs']['overall']['success rate'] = overall
        results['jobs']['overall']['tempest builds'] = tt
        results['jobs']['overall']['total jobs'] = td

        # write to file
        oil_stats_path = os.path.join(where, "oil-stats.yaml")
        with open(oil_stats_path, "w") as output:
            output.write(yaml.safe_dump(results))
        return (results, oil_stats_path)
        
    def create_mock_bug_tuple(self):
        number_of_significant_figs = 5 
        multiplier = 10 ** number_of_significant_figs
        mock_bug_no = round(random() * multiplier)
        integer = randint(1, 25)
        return (mock_bug_no, integer)

    def create_mock_bugs_dict(self):
        mock_bugs = []
        for n in range(randint(1, 10)):
            mock_bugs.append(self.create_mock_bug_tuple())
        return {mock_bug_no: integer for mock_bug_no, integer in mock_bugs}
        
    def create_bug_ranking_yml(self, where, name):
        results = self.create_mock_bugs_dict()
        rank_yaml_path = os.path.join(where, name)
        with open(rank_yaml_path, "w") as output:
            output.write(yaml.safe_dump(results))
        return (results, rank_yaml_path)

    def create_mock_scp_data(self, env_name, folder=None, when='now'):
        folder = tempfile.mktemp() if folder is None else folder
        mock_data_path = os.path.join(folder, env_name)
        daily_path = os.path.join(mock_data_path, 'daily')
        weekly_path = os.path.join(mock_data_path, 'weekly')
        
        mock_files = {}

        for path in [daily_path, weekly_path]:
            self.makedirs(path)
            ts_loc = self.create_timestamp_file(path, when)
            results, oil_stats_path = self.create_oil_stats_yaml(path)
            deploy_results, deploy_bug_rank_loc = \
                self.create_bug_ranking_yml(path, 
                                            "bug_ranking_pipeline_deploy.yml")
            prepare_results, prepare_bug_rank_loc = \
                self.create_bug_ranking_yml(path, 
                                            "bug_ranking_pipeline_prepare.yml")
            tempest_results, tempest_bug_rank_loc = \
                self.create_bug_ranking_yml(path, 
                    "bug_ranking_test_tempest_smoke.yml")

        yaml_file = self.create_report_status(mock_data_path)
        
        import pdb; pdb.set_trace()
        
        return (oil_stats_path, deploy_bug_rank_loc, prepare_bug_rank_loc, 
                tempest_bug_rank_loc, yaml_file)


    def destroy_mock_data(self, env_name, folder):
        import pdb; pdb.set_trace()

