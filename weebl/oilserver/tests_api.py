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

    def post_create_model(self, model, data={}, status_code=False):
        response = self.api_client.post(
            '/api/{}/{}/'.format(self.version, model), data=data)
        if status_code:
            return (self.deserialize(response), response.status_code)
        else:
            return self.deserialize(response)

class EnvironmentResourceTest(ResourceTests):

    def setUp(self):
        super(EnvironmentResourceTest, self).setUp()

    def post_create_environment_model_with_name(self, name=None,
                                                status_code=False):
        if name is None:
            name = utils.generate_uuid()
        data = {'name': name}
        return self.post_create_model('environment', data=data,
                                      status_code=status_code)

    def test_get_all_environment_models(self):
        '''GET all environment models.'''
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
        self.assertEqual(response.status_code, 200)

    def test_get_specific_environment_model(self):
        '''GET a specific environment model by it's UUID.'''
        r_dict0 = self.post_create_environment_model_with_name()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/environment/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)

        # Assertions
        self.assertEquals(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200)

    def test_get_specific_environment_model_by_name(self):
        '''GET a specific environment model by it's name.'''
        name = "mock_production"
        r_dict0 = self.post_create_environment_model_with_name(name)
        response = self.api_client.get('/api/{}/environment/by_name/{}/'
                                       .format(self.version, name),
                                       format='json')
        r_dict1 = self.deserialize(response)

        # Assertions
        self.assertEquals(r_dict0, r_dict1)
        self.assertEqual(response.status_code, 200)

    def test_post_create_environment_model(self):
        '''POST to create a new environment model.'''
        r_dict, status_code =\
            self.post_create_environment_model_with_name(status_code=True)
        new_obj = Environment.objects.filter(uuid=r_dict['uuid'])

        # Assertions
        self.assertIn('uuid', r_dict)
        self.assertNotEqual(new_obj.count(), 0)
        self.assertEqual(status_code, 201)

    def test_put_update_existing_environment_model(self):
        '''PUT to update an existing environment model.'''
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
        self.assertEqual(response.status_code, 200)

    def test_delete_environment_model(self):
        '''DELETE an existing environment model.'''

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


class ServiceStatusResourceTest(ResourceTests):

    def setUp(self):
        super(ServiceStatusResourceTest, self).setUp()

    def test_get_all_service_status_models(self):
        '''GET all service_status models.
        Initial service_status objects should have been loaded in via fixtures.
        '''
        response =\
            self.api_client.get('/api/{}/service_status/'.format(self.version))
        r_dict = self.deserialize(response)
        obj_names = [x['name'] for x in r_dict['objects']]

        # Assertions
        self.assertIn('up', obj_names)
        self.assertIn('unstable', obj_names)
        self.assertIn('down', obj_names)
        self.assertIn('unknown', obj_names)
        self.assertEqual(response.status_code, 200)

    def test_post_method_not_allowed(self):
        '''Validate that user cannot POST service_status model.'''
        response = self.api_client.post('/api/{}/service_status/'
                                        .format(self.version))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_put_method_not_allowed(self):
        '''Validate that user cannot PUT service_status model.'''
        response = self.api_client.put('/api/{}/service_status/'
                                        .format(self.version))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_delete_method_not_allowed(self):
        '''Validate that user cannot DELETE a specific service_status model.'''
        response = self.api_client.delete('/api/{}/service_status/0/'
                                        .format(self.version))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 404)


class JenkinsResourceTest(ResourceTests):

    def setUp(self):
        super(JenkinsResourceTest, self).setUp()
        self.unrecognied_environment_uuid_msg =\
            {'error': ''}  # This really needs to be changed! 

    def test_put_mock_jenkins_check_in_with_new_environment_uuid(self):
        '''Attempting to call jenkins API with new environment uuid should fail
        as the create new envrionment call needs to be called first, but it
        should fail with the correct error message.
        '''
        env_uuid = utils.generate_uuid()
        response = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, env_uuid))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertEqual(r_dict, self.unrecognied_environment_uuid_msg)
        self.assertEqual(response.status_code, 400)


    def test_put_mock_jenkins_check_in_with_existing_uuid(self):
        '''Attempting to call jenkins API with new environment uuid should fail
        as the create new envrionment call needs to be called first, but it
        should fail with the correct error message.
        '''
        
        env_uuid = utils.generate_uuid()
        response1 = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, env_uuid))
        r_dict1 = self.deserialize(response1)
        correct_msg = r_dict1 == self.unrecognied_environment_uuid_msg
        
        # Create a new environment:
        response2 = self.api_client.post(
            '/api/{}/environment/'.format(self.version, env_uuid))
        r_dict1 = self.deserialize(response1)
        correct_msg = r_dict1 == self.unrecognied_environment_uuid_msg

        import pdb; pdb.set_trace()
        
        
        
        # From find by name (above):
        #
        #name = "mock_production"
        #r_dict0 = self.post_create_environment_model_with_name(name)
        #response = self.api_client.get('/api/{}/environment/by_name/{}/'
        #                               .format(self.version, name),
        #                               format='json')
        #r_dict1 = self.deserialize(response)      
        
        
        
        
        # 
        post_create_model(self, model, data={}, status_code=False)
        

        # Assertions
        self.assertTrue(correct_msg)
        self.assertEqual(r_dict, self.unrecognied_environment_uuid_msg)
        self.assertEqual(response.status_code, 400)



        # Confirm error message (400)
        response
        post_create_model(self, model, data={}, status_code=False)
        # Create new environment first, then resend
