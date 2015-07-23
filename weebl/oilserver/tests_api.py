#! /usr/bin/env python3
import utils
from tastypie.test import ResourceTestCase
from weebl import urls
from oilserver import models


class ResourceTests(ResourceTestCase):
    version = urls.v_api.api_name
    fixtures = ['initial_settings.yaml']

    def post_create_model_with_status_code(self, model, data):
        response = self.api_client.post(
            '/api/{}/{}/'.format(self.version, model), data=data)
        return (self.deserialize(response), response.status_code)

    def post_create_model_without_status_code(self, model, data={}):
        response = self.api_client.post(
            '/api/{}/{}/'.format(self.version, model), data=data)
        return self.deserialize(response)


class EnvironmentResourceTest(ResourceTests):

    def setUp(self):
        super(EnvironmentResourceTest, self).setUp()

    def post_create_environment_model_with_name(self, name=None):
        if name is None:
            name = utils.generate_random_string()
        data = {'name': name}
        return self.post_create_model_without_status_code('environment',
                                                          data=data)

    def test_get_all_environment_models(self):
        """GET all environment models."""
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
        """GET a specific environment model by it's UUID."""
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
        """GET a specific environment model by it's name."""
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
        """POST to create a new environment model."""
        r_dict, status_code = self.post_create_model_with_status_code(
            'environment',
            data={'name': utils.generate_random_string()})
        new_obj = models.Environment.objects.filter(uuid=r_dict['uuid'])

        # Assertions
        self.assertIn('uuid', r_dict)
        self.assertNotEqual(new_obj.count(), 0)
        self.assertEqual(status_code, 201)

    def test_put_update_existing_environment_model(self):
        """PUT to update an existing environment model."""
        r_dict = self.post_create_environment_model_with_name()
        uuid = r_dict['uuid']
        new_name = utils.generate_random_string()
        data = {'name': new_name}

        response = self.api_client.put('/api/{}/environment/{}/'
                                       .format(self.version, uuid), data=data)
        new_r_dict = self.deserialize(response)

        # Assertions
        self.assertEquals(r_dict['uuid'], new_r_dict['uuid'])
        self.assertNotEquals(r_dict['name'], new_r_dict['name'])
        self.assertEqual(response.status_code, 200)

    def test_put_cannot_update_existing_environment_models_uuid(self):
        """PUT to update an existing environment model."""
        r_dict = self.post_create_environment_model_with_name()
        uuid = r_dict['uuid']
        new_uuid = utils.generate_uuid()
        new_name = utils.generate_random_string()
        data = {'uuid': new_uuid, 'name': new_name}

        response = self.api_client.put('/api/{}/environment/{}/'
                                       .format(self.version, uuid), data=data)
        new_r_dict = self.deserialize(response)

        # Assertions
        self.assertEquals(uuid, new_r_dict['uuid'])
        self.assertNotEquals(new_uuid, new_r_dict['uuid'])
        self.assertNotEquals(r_dict['name'], new_r_dict['name'])
        self.assertEqual(response.status_code, 200)

    def test_delete_environment_model(self):
        """DELETE an existing environment model."""

        r_dict0 = self.post_create_environment_model_with_name()
        uuid = r_dict0['uuid']
        obj_created = models.Environment.objects.filter(uuid=uuid).count() > 0

        response = self.api_client.delete('/api/{}/environment/{}/'
                                          .format(self.version, uuid))

        non_obj = models.Environment.objects.filter(uuid=uuid)

        # Assertions
        self.assertTrue(obj_created)
        self.assertEqual(non_obj.count(), 0)
        self.assertEqual(response.status_code, 204)


class ServiceStatusResourceTest(ResourceTests):

    def setUp(self):
        """Initial service_status objects should have been loaded in via
        fixtures.
        """
        super(ServiceStatusResourceTest, self).setUp()

    def test_get_method_not_allowed(self):
        """Validate that user cannot GET service_status model."""
        response =\
            self.api_client.get('/api/{}/service_status/'.format(self.version))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_post_method_not_allowed(self):
        """Validate that user cannot POST service_status model."""
        response = self.api_client.post('/api/{}/service_status/'
                                        .format(self.version))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_put_method_not_allowed(self):
        """Validate that user cannot PUT service_status model."""
        response = self.api_client.put('/api/{}/service_status/'
                                        .format(self.version))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_delete_method_not_allowed(self):
        """Validate that user cannot DELETE a specific service_status model."""
        response = self.api_client.delete('/api/{}/service_status/0/'
                                        .format(self.version))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)


class JenkinsResourceTest(ResourceTests):

    def setUp(self):
        super(JenkinsResourceTest, self).setUp()
        self.unrecognied_environment_uuid_msg =\
            {'error': ''}  # TODO: This really needs to be changed!

    def create_new_environment_and_jenkins_with_random_name(self):
        random_name = utils.generate_random_string()
        random_url = utils.generate_random_url()
        data1 = {'name': random_name}
        response1 = self.post_create_model_without_status_code('environment',
                                                               data=data1)
        uuid = response1['uuid']
        data2 = {'environment': uuid, 'external_access_url': random_url}
        response2 = self.post_create_model_without_status_code('jenkins',
                                                               data=data2)
        return (uuid, random_name)

    def test_put_mock_jenkins_check_in_with_new_environment_uuid(self):
        """Attempting to call jenkins API with new environment uuid should fail
        as the create new envrionment call needs to be called first, but it
        should fail with the correct error message.
        """
        env_uuid = utils.generate_uuid()
        response = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, env_uuid))
        r_dict = self.deserialize(response)

        # Assertions
        self.assertEqual(r_dict, self.unrecognied_environment_uuid_msg)
        self.assertEqual(response.status_code, 400)

    def test_put_mock_jenkins_check_in_with_existing_uuid(self):
        """Attempting to call jenkins API with an existing environment uuid
        should return with the correct .
        """
        uuid, random_name =\
            self.create_new_environment_and_jenkins_with_random_name()

        # GET UUID for random_name:
        response1 = self.api_client.get('/api/{}/environment/by_name/{}/'
                                        .format(self.version, random_name),
                                        format='json')
        r_dict1 = self.deserialize(response1)
        returned_uuid = r_dict1['uuid']
        uuids_match = (uuid == returned_uuid)

        # Update status via PUT request (check in):
        response2 = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, returned_uuid),
            data={},
            format='json')
        r_dict2 = self.deserialize(response2)
        timestamp = r_dict2['service_status_updated_at']
        lt_than_1_min = utils.time_difference_less_than_x_mins(timestamp, 1)

        # Assertions
        self.assertTrue(uuids_match)
        self.assertTrue(utils.uuid_check(returned_uuid))
        self.assertTrue(lt_than_1_min)
        self.assertEqual(response2.status_code, 200)


    def test_put_mock_jenkins_check_in_with_data(self):
        """Attempting to call jenkins API with an existing environment uuid
        should return with the correct .
        """
        uuid, random_name =\
            self.create_new_environment_and_jenkins_with_random_name()
        inturl = utils.generate_random_url()
        exturl = utils.generate_random_url()

        # GET UUID for random_name:
        response1 = self.api_client.get('/api/{}/environment/by_name/{}/'
                                        .format(self.version, random_name),
                                        format='json')
        r_dict1 = self.deserialize(response1)
        returned_uuid = r_dict1['uuid']
        uuids_match = (uuid == returned_uuid)

        # Update status via PUT request (check in):
        response2 = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, returned_uuid),
            data={"external_access_url": exturl,
                  "internal_access_url": inturl},
            format='json')
        r_dict2 = self.deserialize(response2)
        timestamp = r_dict2['service_status_updated_at']
        lt_than_1_min = utils.time_difference_less_than_x_mins(timestamp, 1)

        # Assertions
        self.assertTrue(lt_than_1_min)
        self.assertEqual(response2.status_code, 200)
        self.assertTrue(r_dict2['internal_access_url'] == inturl)
        self.assertTrue(r_dict2['external_access_url'] == exturl)


class BuildExecutorTest(ResourceTests):

    def setUp(self):
        super(BuildExecutorTest, self).setUp()

    def create_new_environment_and_jenkins(self):
        random_name = utils.generate_random_string()
        random_url = utils.generate_random_url()
        data1 = {'name': random_name}
        response1 = self.post_create_model_without_status_code('environment',
                                                               data=data1)
        uuid = response1['uuid']
        data2 = {'environment': uuid, 'external_access_url': random_url}
        response2 = self.post_create_model_without_status_code('jenkins',
                                                               data=data2)
        return (uuid, random_name)

    def post_create_build_executor_model_with_name(self, name=None):
        if name is None:
            name = utils.generate_random_string()
        uuid, env_name = self.create_new_environment_and_jenkins()

        data = {'name': name, 'jenkins': uuid}
        return self.post_create_model_without_status_code(
            'build_executor', data=data)

    def test_post_create_build_executor_model(self):
        uuid, env_name = self.create_new_environment_and_jenkins()

        name = utils.generate_random_string()
        data = {'name': name, 'jenkins': uuid}
        r_dict, status_code = self.post_create_model_with_status_code(
            'build_executor', data=data)

        # Assertions
        self.assertIn('uuid', r_dict)
        self.assertNotIn('pk', r_dict)
        self.assertEqual(r_dict['name'], name)
        self.assertNotEqual(r_dict['uuid'], uuid)
        self.assertEqual(status_code, 201)

    def test_get_all_build_executor_models(self):
        """GET all build_executor models."""
        r_dict0 = self.post_create_build_executor_model_with_name('mock_bex0')
        r_dict1 = self.post_create_build_executor_model_with_name('mock_bex1')
        r_dict2 = self.post_create_build_executor_model_with_name('mock_bex2')
        response = self.api_client.get('/api/{}/build_executor/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']

        # Assertions
        self.assertIn(r_dict0['uuid'], objects[0]['uuid'])
        self.assertIn(r_dict1['uuid'], objects[1]['uuid'])
        self.assertIn(r_dict2['uuid'], objects[2]['uuid'])
        self.assertEqual(response.status_code, 200)

    def test_get_specific_build_executor_model(self):
        """GET a specific build_executor model by it's UUID."""
        r_dict0 = self.post_create_build_executor_model_with_name()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/build_executor/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)

        # Assertions
        self.assertEquals(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200)

    def test_put_update_existing_build_executor_model(self):
        """PUT to update an existing build_executor model."""
        r_dict = self.post_create_build_executor_model_with_name()
        uuid = r_dict['uuid']
        new_name = utils.generate_random_string()
        data = {'name': new_name}

        response = self.api_client.put('/api/{}/build_executor/{}/'
                                       .format(self.version, uuid), data=data)
        new_r_dict = self.deserialize(response)

        # Assertions
        self.assertNotEquals(r_dict['name'], new_r_dict['name'])
        self.assertEqual(response.status_code, 200)

    def test_put_cannot_update_existing_build_executor_models_uuid(self):
        """PUT to update an existing build_executor model."""
        r_dict = self.post_create_build_executor_model_with_name()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        new_name = utils.generate_random_string()
        data = {'uuid': uuid2, 'name': new_name}

        response = self.api_client.put('/api/{}/build_executor/{}/'
                                       .format(self.version, uuid), data=data)
        new_r_dict = self.deserialize(response)

        # Assertions
        self.assertEquals(uuid, new_r_dict['uuid'])
        self.assertNotEquals(uuid2, new_r_dict['uuid'])
        self.assertNotEquals(r_dict['name'], new_r_dict['name'])
        self.assertEqual(response.status_code, 200)

    def test_delete_build_executor_model(self):
        """DELETE an existing build_executor model."""

        r_dict0 = self.post_create_build_executor_model_with_name()
        uuid = r_dict0['uuid']
        obj_created =\
            models.BuildExecutor.objects.filter(uuid=uuid).count() > 0
        response = self.api_client.delete('/api/{}/build_executor/{}/'
                                          .format(self.version, uuid))

        non_obj = models.BuildExecutor.objects.filter(uuid=uuid)

        # Assertions
        self.assertTrue(obj_created)
        self.assertEqual(non_obj.count(), 0)
        self.assertEqual(response.status_code, 204)


class PipelineTest(ResourceTests):

    def setUp(self):
        super(PipelineTest, self).setUp()

    def create_new_environment_jenkins_and_build_executor(self):
        # Create environment:
        random_env_name = utils.generate_random_string()
        random_url = utils.generate_random_url()
        data1 = {'name': random_env_name}
        response1 = self.post_create_model_without_status_code(
            'environment', data=data1)

        # Create jenkins:
        uuid = response1['uuid']
        data2 = {'environment': uuid, 'external_access_url': random_url}
        response2 = self.post_create_model_without_status_code(
            'jenkins', data=data2)

        # Create build executor:
        random_buildex_name = utils.generate_random_string()
        data3 = {'name': random_buildex_name, 'jenkins': uuid}
        response3 = self.post_create_model_without_status_code(
            'build_executor', data=data3)

        return response3['uuid']

    def test_post_create_build_executor_model(self):
        buildex = self.create_new_environment_jenkins_and_build_executor()

        data = {'build_executor': buildex}
        r_dict, status_code = self.post_create_model_with_status_code(
            'pipeline', data=data)

        # Assertions
        self.assertIn('pipeline_id', r_dict)
        self.assertNotIn('pk', r_dict)
        self.assertEqual(status_code, 201)

    def test_get_all_pipeline_models(self):
        """GET all pipeline models."""
        buildex = self.create_new_environment_jenkins_and_build_executor()
        data = {'build_executor': buildex}
        r_dict0 = self.post_create_model_without_status_code(
            'pipeline', data=data)
        r_dict1 = self.post_create_model_without_status_code(
            'pipeline', data=data)
        r_dict2 = self.post_create_model_without_status_code(
            'pipeline', data=data)

        response = self.api_client.get('/api/{}/pipeline/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']

        # Assertions
        self.assertIn(r_dict0['pipeline_id'], objects[0]['pipeline_id'])
        self.assertIn(r_dict1['pipeline_id'], objects[1]['pipeline_id'])
        self.assertIn(r_dict2['pipeline_id'], objects[2]['pipeline_id'])
        self.assertEqual(response.status_code, 200)

    def test_get_specific_pipeline_model(self):
        """GET a specific pipeline model by it's UUID."""
        buildex = self.create_new_environment_jenkins_and_build_executor()
        data = {'build_executor': buildex}
        r_dict0, status_code = self.post_create_model_with_status_code(
            'pipeline', data=data)
        pipeline_id = r_dict0['pipeline_id']
        response = self.api_client.get('/api/{}/pipeline/{}/'
                                       .format(self.version, pipeline_id),
                                       format='json')
        r_dict1 = self.deserialize(response)

        # Assertions
        self.assertEquals(pipeline_id, r_dict1['pipeline_id'])
        self.assertEqual(response.status_code, 200)

    def test_put_method_not_allowed(self):
        """PUT to update an existing pipeline model."""
        buildex = self.create_new_environment_jenkins_and_build_executor()
        data = {'build_executor': buildex}
        r_dict0, status_code = self.post_create_model_with_status_code(
            'pipeline', data=data)
        pipeline_id = r_dict0['pipeline_id']
        data = {}
        response = self.api_client.put('/api/{}/pipeline/{}/'
                                       .format(self.version, pipeline_id),
                                       data=data, format='json')
        r_dict1 = self.deserialize(response)

        # Assertions
        self.assertIsNone(r_dict1)
        self.assertEqual(response.status_code, 405)

    def test_delete_pipeline_model(self):
        """DELETE an existing pipeline model."""
        buildex = self.create_new_environment_jenkins_and_build_executor()
        data = {'build_executor': buildex}
        r_dict0, status_code = self.post_create_model_with_status_code(
            'pipeline', data=data)
        pipeline_id = r_dict0['pipeline_id']

        obj_created =\
            models.Pipeline.objects.filter(pipeline_id=pipeline_id).count() > 0
        response = self.api_client.delete('/api/{}/pipeline/{}/'
                                       .format(self.version, pipeline_id),
                                       format='json')

        non_obj = models.Pipeline.objects.filter(pipeline_id=pipeline_id)

        # Assertions
        self.assertTrue(obj_created)
        self.assertEqual(non_obj.count(), 0)
        self.assertEqual(response.status_code, 204)
