#! /usr/bin/env python3
import utils
from tastypie.test import ResourceTestCase
from weebl import urls
from oilserver.models import (
    WeeblSetting,
    Environment,
    ServiceStatus,
    Jenkins)

class ResourceTests(ResourceTestCase):
    version = urls.v_api.api_name
    fixtures = ['initial_settings.yaml']

class EnvironmentResourceTest(ResourceTests):

    def setUp(self):
        super(EnvironmentResourceTest, self).setUp()

    def post_create_environment_model_with_name(self, name=None):
        if name is None:
            name = utils.generate_uuid()
        data = {'name': name}
        return self.post_create_environment_model(data)

    def post_create_environment_model(self, data={}):
        response = self.api_client.post('/api/{}/environment/'
                                       .format(self.version), data=data)
        return self.deserialize(response)

    def test_get_all_environment_models(self):
        ''' GET all environment models.'''
        r_dict0 = self.post_create_environment_model_with_name('mock_env0')
        r_dict1 = self.post_create_environment_model_with_name('mock_env1')
        r_dict2 = self.post_create_environment_model_with_name('mock_env2')
        response = self.api_client.get('/api/{}/environment/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']

        # Assertions
        self.assertIn(r_dict0['uuid'], objects[0]['uuid'])
        self.assertIn(r_dict1['uuid'], objects[1]['uuid'])
        self.assertIn(r_dict2['uuid'], objects[2]['uuid'])

    def test_get_specific_environment_models(self):
        ''' GET a specific environment model by it's UUID.'''
        r_dict = self.post_create_environment_model_with_name()
        uuid = r_dict['uuid']
        response = self.api_client.get('/api/{}/environment/{}/'
                                       .format(self.version, uuid),
                                       format='json')

        # Assertions
        self.assertEquals(uuid, r_dict['uuid'])

    def test_post_create_environment_model(self):
        ''' POST to create a new environment model.'''
        r_dict = self.post_create_environment_model_with_name()
        new_obj = Environment.objects.filter(uuid=r_dict['uuid'])

        # Assertions
        self.assertIn('uuid', r_dict)
        self.assertNotEqual(new_obj.count(), 0)

    def test_put_update_existing_environment_model(self):
        ''' PUT to update an existing environment model.'''
        r_dict = self.post_create_environment_model_with_name()
        uuid = r_dict['uuid']
        new_name = utils.generate_uuid()
        data = {'uuid': uuid, 'name': new_name}

        response = self.api_client.put('/api/{}/environment/{}/'
                                       .format(self.version, uuid), data=data)
        new_r_dict = self.deserialize(response)

        # Assertions
        self.assertEquals(r_dict['uuid'], new_r_dict['uuid'])
        self.assertNotEquals(r_dict['name'], new_r_dict['name'])

    def test_delete_environment_model(self):
        ''' DELETE an existing environment model.'''

        r_dict0 = self.post_create_environment_model_with_name()
        uuid = r_dict0['uuid']
        obj_created = Environment.objects.filter(uuid=uuid).count() > 0

        response = self.api_client.delete('/api/{}/environment/{}/'
                                          .format(self.version, uuid))

        non_obj = Environment.objects.filter(uuid=uuid)
        
        # Assertions
        self.assertTrue(obj_created)
        self.assertEqual(non_obj.count(), 0)
        self.assertEqual(response.status_code, 204)
