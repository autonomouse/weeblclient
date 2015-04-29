import os
import tempfile
import yaml
from django.test import TestCase
from datetime import datetime
from dateutil.parser import parse

class WeeblTestCase(TestCase):
    # Helper methods:
    def mock_batch_oil_stats_data(self):
        pass
        
    def makedirs(self, path):
        try:
            os.makedirs(path)
        except OSError:
            pass
    
    def create_temporary_yaml_file(self, dictionary):
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(yaml.dump(dictionary))
            temp.flush()
        return temp.name
    
    def write_to_file(self, path_to_file, text):
        with open(path_to_file, 'w') as f:
            f.write(text)
        
    def get_timestamp(self, when):
        if when == 'now':
            timestamp = datetime.now()
        else:
            timestamp = parse(when)
        return timestamp.strftime('%F_%T')
        
    def create_timestamp_file(self, where, when):
        write_to_file(self.get_timestamp(when))
        
    def create_oil_stats_yaml(self, where):
        import pdb; pdb.set_trace()
        
    def create_pipeline_deploy_bug_ranking_yml(self, where):
        import pdb; pdb.set_trace()
        
    def create_pipeline_prepare_bug_ranking_yml(self, where):
        import pdb; pdb.set_trace()
        
    def create_test_tempest_smoke_bug_ranking_yml(self, where): 
        import pdb; pdb.set_trace()
    
    def create_mock_data(self, env_name, folder, when='now'):
        mock_data_path = os.path.join(folder, env_name)
        daily_path = os.path.join(mock_data_path, 'daily')
        weekly_path = os.path.join(mock_data_path, 'weekly') 
        
        for path in [daily_path, weekly_path]:
            self.makedirs(path)
            self.create_timestamp_file(path, when)
            import pdb; pdb.set_trace()
            self.create_oil_stats_yaml(path)
            self.create_pipeline_deploy_bug_ranking_yml(path)
            self.create_pipeline_prepare_bug_ranking_yml(path)
            self.create_test_tempest_smoke_bug_ranking_yml(path)     
        
        
        
        
        
        

        
        
        import pdb; pdb.set_trace()
        
        
        yaml_file = self.create_temporary_yaml_file(a_dictionary)
        
                
    def destroy_mock_data(self, env_name, folder):
        import pdb; pdb.set_trace()
        
