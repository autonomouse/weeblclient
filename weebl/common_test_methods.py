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
