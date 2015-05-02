#! /usr/bin/env python3
import os
import shutil
from oilserver import views
from django.http import HttpRequest
from common_test_methods import WeeblTestCase
from collections import namedtuple


class DevSmokeTests(WeeblTestCase):

    def test_main_page(self):
        request = HttpRequest()
        response = views.main_page(request)
        self.assertIn(b'Filters', response.content)
        self.assertIn(b'Breakdown by category', response.content)
        self.assertIn(b'Top ten', response.content)

    def test_job_specific_bugs_list(self):
        request = HttpRequest()
        job = 'pipeline_deploy'
        response = views.job_specific_bugs_list(request, job)
        self.assertIn(b'All', response.content)


class UnitTests(WeeblTestCase):

    def test_load_from_yaml_file(self):
        # Create mock data:
        a_dictionary = {'a': 1, 'b': 2, 'c': 3}
        file_loc = self.create_temporary_yaml_file('yaml.yaml', a_dictionary)

        # Test method:
        oil_yaml = views.load_from_yaml_file(file_loc)

        # Tidy Up:
        os.remove(file_loc)

        # Assertion
        self.assertEquals(a_dictionary, oil_yaml)

    def test_get_current_oil_state_up(self):
        # Give the env_name the same name as this method:
        env_name = str(self).split(' ')[0]

        # Create mock data:
        frmt = '%Y-%m-%d %H:%M:%S'
        report = {"dead_nodes": [],
                   "build_hanging_time_threshold": 10800,
                   "last_time_jenkins_reported": self.time_now(frmt),
                   "start_builds_queue": [q for q in range(1, 10)]}
        mock_file_data = self.create_mock_scp_data(env_name, report=report)
        data_location = mock_file_data['mock_data_path']
        input_env = namedtuple('env', '')

        # Test method:
        output_env = views.get_current_oil_state(data_location, input_env)
        dead_nodes = [msg for msg in output_env.oil_situation if 'dead' in msg]
        check_in = [msg for msg in output_env.oil_situation if 'days' in msg]

        # Tidy Up:
        rootdir = os.path.abspath(os.path.join(
                               mock_file_data['mock_data_path'], '..'))
        shutil.rmtree(rootdir)

        # Assertions
        self.assertEquals(output_env.oil_state, 'up')
        self.assertEqual(dead_nodes, [])
        self.assertEqual(check_in, [])

    def test_get_current_oil_state_down(self):
        # Give the env_name the same name as this method:
        env_name = str(self).split(' ')[0]

        # Create mock data:
        node_test_name = 'master'
        report = {"dead_nodes": [node_test_name],
                   "build_hanging_time_threshold": 10800,
                   "last_time_jenkins_reported": "2000-01-01 00:00:00",
                   "start_builds_queue": [q for q in range(1, 10)]}
        mock_file_data = self.create_mock_scp_data(env_name, report=report)
        data_location = mock_file_data['mock_data_path']
        input_env = namedtuple('env', '')

        # Test method:
        output_env = views.get_current_oil_state(data_location, input_env)
        dead_nodes = [msg for msg in output_env.oil_situation if 'dead' in msg]
        check_in = [msg for msg in output_env.oil_situation if 'days' in msg]

        # Tidy Up:
        rootdir = os.path.abspath(os.path.join(
                               mock_file_data['mock_data_path'], '..'))
        shutil.rmtree(rootdir)

        # Assertions
        self.assertEquals(output_env.oil_state, 'down')
        self.assertIn(node_test_name, dead_nodes[0])
        self.assertNotEqual(check_in, [])

    def test_get_current_oil_state_down_out_of_date(self):
        # Give the env_name the same name as this method:
        env_name = str(self).split(' ')[0]

        # Create mock data:
        report = {"dead_nodes": [],
                   "build_hanging_time_threshold": 10800,
                   "last_time_jenkins_reported": "2000-01-01 00:00:00",
                   "start_builds_queue": [q for q in range(1, 10)]}
        mock_file_data = self.create_mock_scp_data(env_name, report=report)
        data_location = mock_file_data['mock_data_path']
        input_env = namedtuple('env', '')

        # Test method:
        output_env = views.get_current_oil_state(data_location, input_env)
        dead_nodes = [msg for msg in output_env.oil_situation if 'dead' in msg]
        check_in = [msg for msg in output_env.oil_situation if 'days' in msg]

        # Tidy Up:
        rootdir = os.path.abspath(os.path.join(
                               mock_file_data['mock_data_path'], '..'))
        shutil.rmtree(rootdir)

        # Assertions
        self.assertEquals(output_env.oil_state, 'down')
        self.assertEqual(dead_nodes, [])
        self.assertNotEqual(check_in, [])

    def test_get_current_oil_state_unstable_dead_node(self):
        # Give the env_name the same name as this method:
        env_name = str(self).split(' ')[0]

        # Create mock data:
        frmt = '%Y-%m-%d %H:%M:%S'
        node_test_name = 'master'
        report = {"dead_nodes": [node_test_name],
                   "build_hanging_time_threshold": 10800,
                   "last_time_jenkins_reported": self.time_now(frmt),
                   "start_builds_queue": [q for q in range(1, 10)]}
        mock_file_data = self.create_mock_scp_data(env_name, report=report)
        data_location = mock_file_data['mock_data_path']
        input_env = namedtuple('env', '')

        # Test method:
        output_env = views.get_current_oil_state(data_location, input_env)
        dead_nodes = [msg for msg in output_env.oil_situation if 'dead' in msg]
        check_in = [msg for msg in output_env.oil_situation if 'days' in msg]

        # Tidy Up:
        rootdir = os.path.abspath(os.path.join(
                               mock_file_data['mock_data_path'], '..'))
        shutil.rmtree(rootdir)

        # Assertions
        self.assertEquals(output_env.oil_state, 'unstable')
        self.assertIn(node_test_name, dead_nodes[0])
        self.assertEqual(check_in, [])

    def test_set_oil_state(self):
        # Create mock data:
        env = namedtuple('env', '')
        env.oil_state = 'up'
        env.oil_situation = []
        new_state = 'down'
        msg = 'New message'

        # Test method:
        views.set_oil_state(env, new_state, msg)

        # Assertions
        self.assertEqual(env.oil_state, new_state)
        self.assertIn(msg, env.oil_situation)

    def test_get_timestamp(self):
        # Create mock data:
        tstamp = self.get_timestamp()
        tframe = namedtuple('env', '')
        tstamp_file_loc = self.create_timestamp_file(where=None, when=tstamp)
        rootdir = os.path.abspath(os.path.join(tstamp_file_loc, '..'))

        # Test method:
        tframe = views.get_timestamp(rootdir, tframe)

        # Tidy Up:
        shutil.rmtree(rootdir)

        # Assertions
        self.assertEqual(tframe.timestamp, tstamp)

    def test_get_bug_ranking_data_obeys_limit(self):
        # Give the env_name the same name as this method:
        env_name = str(self).split(' ')[0]

        # Create mock data:
        limit = 2
        mock_file_data = self.create_mock_scp_data(env_name, report={})
        data_location = os.path.join(mock_file_data['mock_data_path'], 'daily')
        tframe = namedtuple('env', '')

        # Test method:
        tframe = views.get_bug_ranking_data(data_location, tframe, limit)

        # Tidy Up:
        rootdir = os.path.abspath(os.path.join(data_location, '..'))
        shutil.rmtree(rootdir)

        # Assertions
        for job, jlist in tframe.rankings.items():
            self.assertTrue(len(jlist) <= limit)

    def test_get_bug_ranking_data(self):
        # Give the env_name the same name as this method:
        env_name = str(self).split(' ')[0]

        # Create mock data:
        mock_file_data = self.create_mock_scp_data(env_name, report={})
        data_location = os.path.join(mock_file_data['mock_data_path'], 'daily')
        tframe = namedtuple('env', '')
        target = mock_file_data[data_location]['deploy_bug_rank_results']

        # Test method:
        tframe = views.get_bug_ranking_data(data_location, tframe, limit=None)
        outcome = {bug: num for bug, num in tframe.rankings['pipeline_deploy']}

        # Tidy Up:
        rootdir = os.path.abspath(os.path.join(data_location, '..'))
        shutil.rmtree(rootdir)

        # Assertions
        self.assertEqual(target, outcome)
