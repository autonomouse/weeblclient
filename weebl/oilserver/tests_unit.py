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
        # TODO: We need a bit more detail here!
        self.assertIn(b'main_page', response.content)

    def test_job_specific_bugs_list(self):
        request = HttpRequest()
        job = 'pipeline_deploy'
        response = views.job_specific_bugs_list(request, job)
        # TODO: Why does main_page work here?!
        self.assertIn(b'main_page', response.content)


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
        # Create mock data:
        env_name = 'mock_production'
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
        # Create mock data:
        env_name = 'mock_production'
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
        # Create mock data:
        env_name = 'mock_production'
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
        # Create mock data:
        env_name = 'mock_production'
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
        env = namedtuple('env', '')
        env.oil_state = 'up'
        env.oil_situation = []
        new_state = 'down'
        msg = 'New message'
        views.set_oil_state(env, new_state, msg)
        self.assertEqual(env.oil_state, new_state)
        self.assertIn(msg, env.oil_situation)


