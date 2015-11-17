#! /usr/bin/env python3
import utils
from freezegun import freeze_time
from oilserver.tests.common_test_methods import (
    make_bug,
    make_bugoccurrence,
    ResourceTests,
)
from oilserver import models
from oilserver.api.resources import (
    get_bugoccurrence_filters,
)


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
        url = '/api/%s/servicestatus/?meta_only=true' % (self.version)
        response = self.api_client.get(
            url, format='json', authentication=self.get_credentials())
        response_dict = self.deserialize(response)
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        self.assertNotIn('objects', response_dict)


class EnvironmentResourceTest(ResourceTests):
    def test_get_specific_environment_by_name(self):
        """GET a specific environment instance by its name."""
        name = "mock_production"
        r_dict0 = self.make_environment_via_api(name)
        response = self.api_client.get('/api/{}/environment/by_name/{}/'
                                       .format(self.version, name),
                                       format='json',
                                       authentication=self.get_credentials())
        r_dict1 = self.deserialize(response)

        self.assertEqual(r_dict0, r_dict1)
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")


class BugResourceTest(ResourceTests):

    def retrieve_bug(self, uuid):
        url = '/api/%s/bug/%s/' % (self.version, uuid)
        response = self.api_client.get(
            url, format='json', authentication=self.get_credentials())
        self.assertEqual(
            response.status_code, 200, msg='Incorrect status code')
        response_dict = self.deserialize(response)
        return response_dict

    def test_filter_on_bugoccurrences(self):
        """Make sure filtering on bug occurrences for a bug works.

        This tests BugResource.apply_filters.
        """
        bugoccurrence = make_bugoccurrence()
        url = '/api/%s/bug/?knownbugregex__bugoccurrences__uuid=%s' % (
            self.version, bugoccurrence.uuid)
        response = self.api_client.get(
            url, format='json', authentication=self.get_credentials())
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        response_dict = self.deserialize(response)
        self.assertEqual(
            bugoccurrence.regex.bug.uuid,
            response_dict['objects'][0]['uuid'],
            msg="Expected bug from bugoccurrence.")

    def test_includes_bugoccurrence_count_zero(self):
        bug = make_bug()
        response_dict = self.retrieve_bug(bug.uuid)
        self.assertEqual(0, response_dict['occurrence_count'])
        self.assertNotIn('last_seen', response_dict)

    def test_includes_bugoccurrence_count_nonzero(self):
        bugoccurrence = make_bugoccurrence()
        response_dict = self.retrieve_bug(bugoccurrence.regex.bug.uuid)
        self.assertEqual(1, response_dict['occurrence_count'])

    def test_includes_last_seen_time(self):
        first_occurrence = make_bugoccurrence()
        last_occurrence = make_bugoccurrence(regex=first_occurrence.regex)
        response_dict = self.retrieve_bug(first_occurrence.regex.bug.uuid)
        self.assertEqual(
            last_occurrence.build.pipeline.completed_at,
            response_dict['last_seen'])


class EmptyObject(object):
    pass


class FakeQueryDict(dict):
    def getlist(self, key):
        return self[key]

    def setlist(self, key, value):
        if not hasattr(self, 'list_keys'):
            self._list_keys = []
        self._list_keys.append(key)
        self[key] = value


def make_mock_bug_bundle():
    bundle = EmptyObject()
    bundle.obj = make_bug()
    bundle.request = EmptyObject()
    bundle.request.GET = FakeQueryDict()
    return bundle


class GetBugOccurrenceFiltersTest(ResourceTests):
    def test_ignores_non_bug_occurence_filters(self):
        bundle = make_mock_bug_bundle()
        bundle.request.GET['knownbugregex__uuid'] = 'abc'
        filters = get_bugoccurrence_filters(bundle)
        self.assertEqual(
            {'regex__bug__uuid': bundle.obj.uuid},
            filters)

    def test_includes_bug_occurence_filters(self):
        bundle = make_mock_bug_bundle()
        key = 'knownbugregex__bugoccurrences__uuid'
        bundle.request.GET[key] = "abc"
        filters = get_bugoccurrence_filters(bundle)
        expected_filters = {
            'regex__bug__uuid': bundle.obj.uuid,
            'uuid': "abc"
        }
        self.assertEqual(expected_filters, filters)

    def test_includes_bug_occurence_list_filters(self):
        bundle = make_mock_bug_bundle()
        list_key = 'knownbugregex__bugoccurrences__uuid__in'
        bundle.request.GET.setlist(list_key, ['a', 'b'])
        filters = get_bugoccurrence_filters(bundle)
        expected_filters = {
            'regex__bug__uuid': bundle.obj.uuid,
            'uuid__in': ['a', 'b']
        }
        self.assertEqual(expected_filters, filters)
