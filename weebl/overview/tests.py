from django.test import TestCase
from overview.views import (main_page, oil_stats, maintenance_history, tools,
                            job_specific_bugs_list, specific_bug_info,
                            bug_specific_pipelines, event_specific_details,
                            specific_vendor_info, pipeline_specific_bugs,
                            charts, categories_and_tags, bugs_list,
                            vendor_and_hardware, oil_control, 
                            specific_machine_history)
from django.http import HttpRequest

# Create your tests here.
class DevSmokeTests(TestCase):

    def test_main_page(self):
        request = HttpRequest()
        response = main_page(request)
        self.assertIn(b'main_page', response.content)

    def test_oil_stats(self):
        request = HttpRequest()
        response = oil_stats(request)
        self.assertIn(b'oil_stats', response.content)

    def test_job_specific_bugs_list(self):
        request = HttpRequest()
        job = 'pipeline_deploy'
        response = job_specific_bugs_list(request, job)
        self.assertIn(b'job_specific_bugs_list', response.content)
        self.assertIn(b'pipeline_deploy', response.content)

    def test_specific_bug_info(self):
        request = HttpRequest()
        bug = '1234'
        response = specific_bug_info(request, bug)
        self.assertIn(b'specific_bug_info', response.content)
        self.assertIn(b'1234', response.content)

    def test_bug_specific_pipelines(self):
        request = HttpRequest()
        bug = '1234'
        response = bug_specific_pipelines(request, bug)
        self.assertIn(b'bug_specific_pipelines', response.content)
        self.assertIn(b'1234', response.content)

    def test_pipeline_specific_bugs(self):
        request = HttpRequest()
        pipeline = '353d25b4-c2f1-4d6b-990d-469707ed8c51'
        response = pipeline_specific_bugs(request, pipeline)
        self.assertIn(b'pipeline_specific_bugs', response.content)
        self.assertIn(b'353d25b4-c2f1-4d6b-990d-469707ed8c51',
                      response.content)

    def test_maintenance_history(self):
        request = HttpRequest()
        response = maintenance_history(request)
        self.assertIn(b'maintenance_history', response.content)

    def test_event_specific_details(self):
        request = HttpRequest()
        event = '1234'
        response = event_specific_details(request, event)
        self.assertIn(b'event_specific_details', response.content)
        self.assertIn(b'1234', response.content)

    def test_tools(self):
        request = HttpRequest()
        response = tools(request)
        self.assertIn(b'tools', response.content)

    def test_specific_vendor_info(self):
        request = HttpRequest()
        vendor = 'Dell'
        response = specific_vendor_info(request, vendor)
        self.assertIn(b'specific_vendor_info', response.content)
        self.assertIn(b'Dell', response.content)

    def test_charts(self):
        request = HttpRequest()
        response = charts(request)
        self.assertIn(b'charts', response.content)

    def test_categories_and_tags(self):
        request = HttpRequest()
        response = categories_and_tags(request)
        self.assertIn(b'categories_and_tags', response.content)

    def test_bugs_list(self):
        request = HttpRequest()
        response = bugs_list(request)
        self.assertIn(b'bugs_list', response.content)

    def test_vendor_and_hardware(self):
        request = HttpRequest()
        response = vendor_and_hardware(request)
        self.assertIn(b'vendor_and_hardware', response.content)

    def test_oil_control(self):
        request = HttpRequest()
        response = oil_control(request)
        self.assertIn(b'oil_control', response.content)

    def test_specific_machine_history(self):
        request = HttpRequest()
        machine = 'hayward-00.oil'
        response = specific_machine_history(request, machine)
        self.assertIn(b'specific_machine_history', response.content)
        self.assertIn(b'hayward-00.oil', response.content)
