import utils
from weebl import urls
from django.test import TestCase
from tastypie.test import ResourceTestCase


class WeeblTestCase(TestCase):
    fixtures = ['initial_settings.yaml']


class ResourceTests(ResourceTestCase):
    version = urls.v_api.api_name
    fixtures = ['initial_settings.yaml']

    def post_create_instance(self, model, data):
        response = self.api_client.post(
            '/api/{}/{}/'.format(self.version, model), data=data)
        return (self.deserialize(response), response.status_code)

    def post_create_instance_without_status_code(self, model, data):
        return self.post_create_instance(model, data)[0]

    def make_environment(self, name=None):
        if name is None:
            name = utils.generate_random_string()
        data = {'name': name}
        return self.post_create_instance_without_status_code(
            'environment', data=data)

    def make_jenkins(self, environment_uuid, url=None):
        if url is None:
            url = utils.generate_random_url()
        data = {'environment': environment_uuid,
                'external_access_url': url}
        return self.post_create_instance_without_status_code(
            'jenkins', data=data)

    def make_environment_and_jenkins(self):
        response1 = self.make_environment()
        env_uuid = response1['uuid']
        env_name = response1['name']
        self.make_jenkins(env_uuid)
        return env_uuid, env_name

    def make_build_executor(self, name=None, env_uuid=None):
        if name is None:
            name = utils.generate_random_string()
        if env_uuid is None:
            env_uuid, env_name = self.make_environment_and_jenkins()
        data = {'name': name,
                'jenkins': env_uuid}
        return self.post_create_instance('build_executor', data=data)

    def make_pipeline(self, buildex=None):
        if buildex is None:
            response = self.make_build_executor()
            buildex = response[0]['uuid']
        data = {'build_executor': buildex}
        return self.post_create_instance('pipeline', data=data)
