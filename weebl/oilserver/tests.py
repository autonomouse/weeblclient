from oilserver.views import (main_page, job_specific_bugs_list)
from django.http import HttpRequest
from common_test_methods import WeeblTestCase


class DevSmokeTests(WeeblTestCase):

    def test_main_page(self):
        request = HttpRequest()
        response = main_page(request)
        self.assertIn(b'main_page', response.content)

    def test_job_specific_bugs_list(self):
        request = HttpRequest()
        job = 'pipeline_deploy'
        response = job_specific_bugs_list(request, job)
        self.assertIn(b'job_specific_bugs_list', response.content)
        self.assertIn(b'pipeline_deploy', response.content)
