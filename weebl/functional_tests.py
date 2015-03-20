import subprocess
import unittest
import time
import shlex
from selenium import webdriver
from django.test import TestCase
import os


class OverviewTestCase(TestCase):

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

    def test_oil_stats(self):
        page_name = 'oil_stats'
        self.driver.get("{}/stats/".format(self.HOST))
        assert page_name in self.driver.title

    def test_job_specific_bugs_list(self):
        page_name = 'job_specific_bugs_list'
        self.driver.get("{}/job/pipeline_deploy".format(self.HOST))
        assert page_name in self.driver.title

    def test_specific_bug_info(self):
        page_name = 'specific_bug_info'
        self.driver.get("{}/bug/1234".format(self.HOST))
        assert page_name in self.driver.title

    def test_bug_specific_pipelines(self):
        page_name = 'bug_specific_pipelines'
        self.driver.get("{}/pipelines/1234".format(self.HOST))
        assert page_name in self.driver.title

    def test_pipeline_specific_bugs(self):
        page_name = 'pipeline_specific_bugs'
        self.driver.get("{}/bugs_hit/353d25b4-c2f1-4d6b-990d-469707ed8c51/"
                        .format(self.HOST))
        assert page_name in self.driver.title

    def test_maintenance_history(self):
        page_name = 'maintenance_history'
        self.driver.get("{}/maintenance/".format(self.HOST))
        assert page_name in self.driver.title

    def test_event_specific_details(self):
        page_name = 'event_specific_details'
        self.driver.get("{}/event/1234".format(self.HOST))
        assert page_name in self.driver.title

    def test_tools(self):
        page_name = 'tools'
        self.driver.get("{}/{}/".format(self.HOST, page_name))
        assert page_name in self.driver.title

    def test_specific_vendor_info(self):
        page_name = 'specific_vendor_info'
        self.driver.get("{}/vendor/Dell".format(self.HOST))
        assert page_name in self.driver.title

    def test_charts(self):
        page_name = 'charts'
        self.driver.get("{}/{}/".format(self.HOST, page_name))
        assert page_name in self.driver.title

    def test_categories_and_tags(self):
        page_name = 'categories_and_tags'
        self.driver.get("{}/{}/".format(self.HOST, page_name))
        assert page_name in self.driver.title

    def test_bugs_list(self):
        page_name = 'bugs_list'
        self.driver.get("{}/{}/".format(self.HOST, page_name))
        assert page_name in self.driver.title

    def test_vendor_and_hardware(self):
        page_name = 'vendor_and_hardware'
        self.driver.get("{}/{}/".format(self.HOST, page_name))
        assert page_name in self.driver.title

    def test_oil_control(self):
        page_name = 'oil_control'
        self.driver.get("{}/{}/".format(self.HOST, page_name))
        assert page_name in self.driver.title

    def test_specific_machine_history(self):
        page_name = 'specific_machine_history'
        self.driver.get("{}/machine/hayward-00.oil".format(self.HOST))
        assert page_name in self.driver.title


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weebl.settings")
    unittest.main()
