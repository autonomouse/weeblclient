#! /usr/bin/env python3
import utils
from freezegun import freeze_time
from common_test_methods import (
    make_bug_occurrence,
    ResourceTests,
)
from oilserver import models


class TimeStampedBaseModelTest(ResourceTests):

    def test_save_generates_timestamps(self):
        with freeze_time("Jan 1 2000 00:00:00"):
            timestamp1 = utils.time_now()
            # Environment uses TimeStampedBaseModel and is easy to
            # make.
            environment = models.Environment(name="environment")
            environment.save()
        self.assertEqual(environment.created_at, timestamp1)
        self.assertEqual(environment.updated_at, timestamp1)
        with freeze_time("Jan 2 2000 00:00:00"):
            timestamp2 = utils.time_now()
            environment.save()
        self.assertEqual(environment.created_at, timestamp1)
        self.assertEqual(environment.updated_at, timestamp2)


class CommonResourceTest(ResourceTests):
    """Test custom code in CommonResource.

    CommonResource isn't a concrete resource, so we can't test it
    directly. These tests will run against resources that inherit it.
    """
    def test_get_meta_only(self):
        """Ensure only meta is returned when meta_only flag is in request."""
        url = '/api/%s/service_status/?meta_only=true' % (self.version)
        response = self.api_client.get(url, format='json')
        response_dict = self.deserialize(response)
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        self.assertNotIn('objects', response_dict)


class EnvironmentResourceTest(ResourceTests):
    def test_get_specific_environment_by_name(self):
        """GET a specific environment instance by its name."""
        name = "mock_production"
        r_dict0 = self.make_environment(name)
        response = self.api_client.get('/api/{}/environment/by_name/{}/'
                                       .format(self.version, name),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(r_dict0, r_dict1)
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")


class BugResourceTest(ResourceTests):
    def test_filter_on_bug_occurrences(self):
        """Make sure filtering on bug occurrences for a bug works.

        This tests BugResource.apply_filters.
        """
        bug_occurrence = make_bug_occurrence()
        url = '/api/%s/bug/?knownbugregex__bug_occurrences__uuid=%s' % (
            self.version, bug_occurrence.uuid)
        response = self.api_client.get(url, format='json')
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        response_dict = self.deserialize(response)
        self.assertEqual(
            bug_occurrence.regex.bug.uuid,
            response_dict['objects'][0]['uuid'],
            msg="Expected bug from bug_occurrence.")