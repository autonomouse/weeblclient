import subprocess
import unittest
import time
import shlex
from selenium import webdriver
from django.test import TestCase
import os


class WebOilTestCase(TestCase):

    SETUP = ['python3 weebl/manage.py syncdb --noinput',]
    RUNSERVER = 'python3 weebl/manage.py runserver'
    HOST = 'http://localhost:8000'

    def setUp(self):

        # Start the server:
        self.setup_django_runserver()
        try:
            self.runserver = self.start_django_runserver()
        except:
            # It's okay if it's already running
            pass

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

    def test_main_page(self):
        page_name = 'main_page'
        self.driver.get("{}/".format(self.HOST))
        assert page_name in self.driver.title

    def test_job_specific_bugs_list(self):
        page_name = 'job_specific_bugs_list'
        self.driver.get("{}/job/pipeline_deploy".format(self.HOST))
        assert page_name in self.driver.title


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weebl.settings")
    unittest.main()
