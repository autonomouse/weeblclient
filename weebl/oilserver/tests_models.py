#! /usr/bin/env python3
from common_test_methods import WeeblTestCase
from oilserver import models
from django.contrib.sites.models import Site


class ModelTests(WeeblTestCase):
    fixtures = ['initial_settings.yaml', ]


class WeeblSettingTests(ModelTests):

    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current().id
        self.settings = models.WeeblSetting.objects.get(pk=self.current_site)

    def test_fields_accessible(self):
        fields = ['site', 'check_in_unstable_threshold',
                  'check_in_down_threshold', 'low_build_queue_threshold',
                  'overall_unstable_th', 'overall_down_th', 'down_colour',
                  'unstable_colour', 'up_colour', 'weebl_documentation',
                  'weebl_version', 'api_version']
        for field in fields:
            self.assertTrue(hasattr(self.settings, field))


class EnvironmentTests(ModelTests):

    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current().id
        self.settings = models.WeeblSetting.objects.get(pk=self.current_site)
        self.environment = models.Environment()
        self.jenkins = models.Jenkins()
        self.jenkins.environment = self.environment

    def test_fields_accessible(self):
        fields = ['uuid', 'name', 'get_set_go', 'state_description', 'state',
                  'state_colour']
        for field in fields:
            self.assertTrue(hasattr(self.environment, field))


class ServiceStatusTests(ModelTests):

    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current().id
        self.settings = models.WeeblSetting.objects.get(pk=self.current_site)
        self.service_status = models.ServiceStatus()

    def test_fields_accessible(self):
        fields = ['name', 'description']
        for field in fields:
            self.assertTrue(hasattr(self.service_status, field))


class JenkinsTests(ModelTests):

    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current().id
        self.settings = models.WeeblSetting.objects.get(pk=self.current_site)
        self.environment = models.Environment()
        self.jenkins = models.Jenkins()
        self.jenkins.environment = self.environment
        self.service_status = models.ServiceStatus()
        self.jenkins.service_status = self.service_status

    def test_fields_accessible(self):
        fields = ['environment', 'service_status', 'external_access_url',
                  'internal_access_url', 'service_status_updated_at', 'uuid']
        for field in fields:
            self.assertTrue(hasattr(self.jenkins, field))


class BuildExecutorTests(ModelTests):

    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current().id
        self.settings = models.WeeblSetting.objects.get(pk=self.current_site)
        self.environment = models.Environment()
        self.jenkins = models.Jenkins()
        self.jenkins.environment = self.environment
        self.service_status = models.ServiceStatus()
        self.jenkins.service_status = self.service_status
        self.build_executor = models.BuildExecutor()
        self.build_executor.jenkins = self.jenkins

    def test_fields_accessible(self):
        fields = ['uuid', 'name', 'jenkins']
        for field in fields:
            self.assertTrue(hasattr(self.build_executor, field))


class PipelineTests(ModelTests):

    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current().id
        self.settings = models.WeeblSetting.objects.get(pk=self.current_site)
        self.environment = models.Environment()
        self.jenkins = models.Jenkins()
        self.jenkins.environment = self.environment
        self.service_status = models.ServiceStatus()
        self.jenkins.service_status = self.service_status
        self.build_executor = models.BuildExecutor()
        self.build_executor.jenkins = self.jenkins
        self.pipeline = models.Pipeline()
        self.pipeline.build_executor = self.build_executor

    def test_fields_accessible(self):
        fields = ['pipeline_id', 'build_executor']
        for field in fields:
            self.assertTrue(hasattr(self.pipeline, field))
