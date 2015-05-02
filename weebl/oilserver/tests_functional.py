#! /usr/bin/env python2

import subprocess
import unittest
import time
import shlex
from selenium import webdriver
from django.test import TestCase
import os


class WebDriverOilTestCase(TestCase):

    SETUP = ['python3 weebl/manage.py syncdb --noinput', ]
    RUNSERVER = 'python3 weebl/manage.py runserver'
    HOST = 'http://localhost:8000'

    def setUp(self):

        # Create mock data:
        self.create_mock_data('test_data')

        # Start the server:
        #self.setup_django_runserver()
        self.runserver = self.start_django_runserver()

        # Create a browser instance and go to site:
        self.driver = webdriver.Firefox()

    def setup_django_runserver(self):
        for cmd in self.SETUP:
            subprocess.check_call(shlex.split(cmd),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

    def start_django_runserver(self):
        p = subprocess.Popen(shlex.split(self.RUNSERVER),
                             stderr=subprocess.STDOUT)
        time.sleep(2)
        return p

    def tearDown(self):
        self.runserver.terminate()
        self.driver.close()

        self.destroy_mock_data('test_data')

'''
class CommonTests(WebDriverOilTestCase):

    def test_deploy_stats(self):
        self.driver.get("{}/".format(self.HOST))
        import pdb; pdb.set_trace()

    def test_prepare_stats(self):
        self.driver.get("{}/".format(self.HOST))
        import pdb; pdb.set_trace()

    def test_tempest_stats(self):
        self.driver.get("{}/".format(self.HOST))
        import pdb; pdb.set_trace()

    def test_state(self):
        self.driver.get("{}/".format(self.HOST))
        import pdb; pdb.set_trace()

    def test_success(self):
        self.driver.get("{}/".format(self.HOST))
        import pdb; pdb.set_trace()


class MainPageTests(WebDriverOilTestCase):

    def test_breakdown(self):
        self.driver.get("{}/".format(self.HOST))
        import pdb; pdb.set_trace()


class JobSpecificBugsListPageTests(WebDriverOilTestCase):

    def test_job_specific_bugs_list(self):
        page_name = 'job_specific_bugs_list'
        self.driver.get("{}/job/pipeline_deploy".format(self.HOST))
        assert page_name in self.driver.title
'''

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weebl.settings")
    unittest.main()
