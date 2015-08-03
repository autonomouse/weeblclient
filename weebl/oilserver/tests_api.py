#! /usr/bin/env python3
import utils
from common_test_methods import ResourceTests
from oilserver import models


class EnvironmentResourceTest(ResourceTests):

    def setUp(self):
        super(EnvironmentResourceTest, self).setUp()

    def test_get_all_environments(self):
        """GET all environment instances."""
        env_dict = []
        mock_envs = ['mock_env0', 'mock_env1', 'mock_env2']
        for mock_env in mock_envs:
            env_dict.append(self.make_environment(mock_env))
        response = self.api_client.get('/api/{}/environment/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']

        self.assertEqual(response.status_code, 200)
        for idx, env in enumerate(env_dict):
            self.assertIn(env['uuid'], objects[idx]['uuid'])

    def test_get_specific_environment(self):
        """GET a specific environment instance by its UUID."""
        r_dict0 = self.make_environment()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/environment/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200)

    def test_get_specific_environment_by_name(self):
        """GET a specific environment instance by its name."""
        name = "mock_production"
        r_dict0 = self.make_environment(name)
        response = self.api_client.get('/api/{}/environment/by_name/{}/'
                                       .format(self.version, name),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(r_dict0, r_dict1)
        self.assertEqual(response.status_code, 200)

    def test_post_create_environment(self):
        """POST to create a new environment instance."""
        r_dict, status_code = self.post_create_instance(
            'environment',
            data={'name': utils.generate_random_string()})
        new_obj = models.Environment.objects.filter(uuid=r_dict['uuid'])

        self.assertIn('uuid', r_dict)
        self.assertNotEqual(new_obj.count(), 0)
        self.assertEqual(status_code, 201)

    def test_put_update_existing_environment(self):
        """PUT to update an existing environment instance."""
        r_dict = self.make_environment()
        uuid = r_dict['uuid']
        new_name = utils.generate_random_string()
        data = {'name': new_name}
        before = models.Environment.objects.filter(name=new_name).exists()
        self.assertFalse(before)

        response = self.api_client.put('/api/{}/environment/{}/'
                                       .format(self.version, uuid), data=data)
        after = models.Environment.objects.filter(name=new_name).exists()
        self.assertTrue(after)
        new_r_dict = self.deserialize(response)
        self.assertEqual(r_dict['uuid'], new_r_dict['uuid'])
        self.assertNotEquals(r_dict['name'], new_r_dict['name'])
        self.assertEqual(response.status_code, 200)

    def test_put_cannot_update_existing_environments_uuid(self):
        """PUT to update an existing environment model."""
        r_dict = self.make_environment()
        uuid = r_dict['uuid']
        new_uuid = utils.generate_uuid()
        data = {'uuid': new_uuid}
        before = models.Environment.objects.filter(uuid=new_uuid).exists()

        response = self.api_client.put('/api/{}/environment/{}/'
                                       .format(self.version, uuid), data=data)
        after = models.Environment.objects.filter(uuid=new_uuid).exists()
        new_r_dict = self.deserialize(response)

        # Assertions
        self.assertEquals(uuid, new_r_dict['uuid'])
        self.assertNotEquals(new_uuid, new_r_dict['uuid'])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(before)
        self.assertFalse(after)

    def test_delete_environment(self):
        """DELETE an existing environment instance."""
        r_dict0 = self.make_environment()
        uuid = r_dict0['uuid']
        obj_created = models.Environment.objects.filter(uuid=uuid).count() > 0
        self.assertTrue(obj_created)

        response = self.api_client.delete('/api/{}/environment/{}/'
                                          .format(self.version, uuid))
        non_obj = models.Environment.objects.filter(uuid=uuid)

        self.assertEqual(non_obj.count(), 0)
        self.assertEqual(response.status_code, 204)


class ServiceStatusResourceTest(ResourceTests):

    def setUp(self):
        """Initial service_status objects should have been loaded in via
        fixtures.
        """
        super(ServiceStatusResourceTest, self).setUp()

    def test_get_method_not_allowed(self):
        """Validate that user cannot GET service_status instance."""
        response =\
            self.api_client.get('/api/{}/service_status/'.format(self.version))

        self.assertIsNone(self.deserialize(response))
        self.assertEqual(response.status_code, 405)

    def test_post_method_not_allowed(self):
        """Validate that user cannot POST service_status instance."""
        response = self.api_client.post('/api/{}/service_status/'
                                        .format(self.version))

        self.assertIsNone(self.deserialize(response))
        self.assertEqual(response.status_code, 405)

    def test_put_method_not_allowed(self):
        """Validate that user cannot PUT service_status instance."""
        response = self.api_client.put('/api/{}/service_status/'
                                       .format(self.version))

        self.assertIsNone(self.deserialize(response))
        self.assertEqual(response.status_code, 405)

    def test_delete_method_not_allowed(self):
        """Validate that user cannot DELETE a specific service_status instance.
        """
        response = self.api_client.delete('/api/{}/service_status/0/'
                                          .format(self.version))

        self.assertIsNone(self.deserialize(response))
        self.assertEqual(response.status_code, 405)


class JenkinsResourceTest(ResourceTests):

    def setUp(self):
        super(JenkinsResourceTest, self).setUp()
        self.unrecognied_environment_uuid_msg =\
            {'error': ''}  # TODO: This really needs to be changed!

    def test_put_mock_jenkins_check_in_with_new_environment_uuid(self):
        """Attempting to call jenkins API with new environment uuid should fail
        as the create new envrionment call needs to be called first, but it
        should fail with the correct error message.
        """
        env_uuid = utils.generate_uuid()
        response = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, env_uuid))
        r_dict = self.deserialize(response)

        self.assertEqual(r_dict, self.unrecognied_environment_uuid_msg)
        self.assertEqual(response.status_code, 400)

    def test_put_mock_jenkins_check_in_with_existing_uuid(self):
        """Attempting to call jenkins API with an existing environment uuid
        should return with the correct .
        """
        uuid, random_name = self.make_environment_and_jenkins()

        # GET UUID for random_name:
        response1 = self.api_client.get('/api/{}/environment/by_name/{}/'
                                        .format(self.version, random_name),
                                        format='json')
        r_dict1 = self.deserialize(response1)
        returned_uuid = r_dict1['uuid']
        self.assertTrue(uuid == returned_uuid)

        # Update status via PUT request (check in):
        response2 = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, returned_uuid),
            data={},
            format='json')
        r_dict2 = self.deserialize(response2)
        timestamp = r_dict2['service_status_updated_at']

        self.assertTrue(utils.uuid_check(returned_uuid))
        self.assertEqual(response2.status_code, 200)
        lt_than_1_min = utils.time_difference_less_than_x_mins(timestamp, 1)
        self.assertTrue(lt_than_1_min)

    def test_put_mock_jenkins_check_in_with_data(self):
        """Attempting to call jenkins API with an existing environment uuid
        should return with the correct .
        """
        uuid, random_name = self.make_environment_and_jenkins()
        inturl = utils.generate_random_url()
        exturl = utils.generate_random_url()

        # GET UUID for random_name:
        response1 = self.api_client.get('/api/{}/environment/by_name/{}/'
                                        .format(self.version, random_name),
                                        format='json')
        r_dict1 = self.deserialize(response1)
        returned_uuid = r_dict1['uuid']
        self.assertTrue(uuid == returned_uuid)

        # Update status via PUT request (check in):
        response2 = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, returned_uuid),
            data={"external_access_url": exturl,
                  "internal_access_url": inturl},
            format='json')
        r_dict2 = self.deserialize(response2)
        timestamp = r_dict2['service_status_updated_at']
        lt_than_1_min = utils.time_difference_less_than_x_mins(timestamp, 1)
        self.assertTrue(lt_than_1_min)
        self.assertEqual(response2.status_code, 200)
        self.assertTrue(r_dict2['internal_access_url'] == inturl)
        self.assertTrue(r_dict2['external_access_url'] == exturl)


class BuildExecutorTest(ResourceTests):

    def setUp(self):
        super(BuildExecutorTest, self).setUp()

    def test_post_create_build_executor(self):
        uuid, name = self.make_environment_and_jenkins()
        r_dict, status_code = self.make_build_executor(
            name=name, env_uuid=uuid)

        self.assertIn('uuid', r_dict)
        self.assertNotIn('pk', r_dict)
        self.assertEqual(r_dict['name'], name)
        self.assertNotEqual(r_dict['uuid'], uuid)
        self.assertEqual(status_code, 201)

    def test_get_all_build_executors(self):
        """GET all build_executor instances."""
        bex_dict = [self.make_build_executor() for _ in range(3)]
        response = self.api_client.get('/api/{}/build_executor/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)

        self.assertEqual(response.status_code, 200)
        expected_uuids = [bdict[0]['uuid'] for bdict in bex_dict]
        actual_uuids = [obj['uuid'] for obj in r_dict['objects']]
        self.assertCountEqual(actual_uuids, expected_uuids)

    def test_get_specific_build_executor(self):
        """GET a specific build_executor instance by its UUID."""
        r_dict0, status_code = self.make_build_executor()
        uuid = r_dict0['uuid']

        response = self.api_client.get('/api/{}/build_executor/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)
        self.assertEqual(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200)

    def test_put_update_existing_build_executor(self):
        """PUT to update an existing build_executor instance."""
        r_dict, status_code = self.make_build_executor()
        uuid = r_dict['uuid']
        new_name = utils.generate_random_string()
        data = {'name': new_name}
        before = models.BuildExecutor.objects.filter(name=new_name).exists()
        self.assertFalse(before)
        response = self.api_client.put('/api/{}/build_executor/{}/'
                                       .format(self.version, uuid), data=data)
        self.assertEqual(response.status_code, 200)
        after = models.BuildExecutor.objects.filter(name=new_name).exists()
        self.assertTrue(after)
        new_r_dict = self.deserialize(response)
        self.assertNotEquals(r_dict['name'], new_r_dict['name'])

    def test_put_cannot_update_existing_build_executors_uuid(self):
        """PUT to update an existing build_executor instance."""
        r_dict, status_code = self.make_build_executor()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        data = {'uuid': uuid2}
        before = models.BuildExecutor.objects.filter(uuid=uuid2).exists()
        self.assertFalse(before)

        response = self.api_client.put('/api/{}/build_executor/{}/'
                                       .format(self.version, uuid), data=data)

        after = models.BuildExecutor.objects.filter(uuid=uuid2).exists()
        self.assertFalse(after, msg="build_executor UUID has been altered!")
        new_r_dict = self.deserialize(response)

        self.assertEqual(uuid, new_r_dict['uuid'])
        self.assertNotEquals(uuid2, new_r_dict['uuid'])
        self.assertEqual(response.status_code, 200)

    def test_delete_build_executor(self):
        """DELETE an existing build_executor instance."""
        r_dict0, status_code = self.make_build_executor()
        uuid = r_dict0['uuid']
        self.assertTrue(models.BuildExecutor.objects.filter(uuid=uuid)
                        .count() > 0, msg="build_executor has not been made")
        response = self.api_client.delete('/api/{}/build_executor/{}/'
                                          .format(self.version, uuid))

        non_obj = models.BuildExecutor.objects.filter(uuid=uuid)
        self.assertEqual(non_obj.count(), 0)
        self.assertEqual(response.status_code, 204)


class PipelineTest(ResourceTests):

    def setUp(self):
        super(PipelineTest, self).setUp()

    def test_post_create_build_executor(self):
        build_executor = self.make_build_executor()[0]['uuid']
        before = str(models.Pipeline.objects.all()) != '[]'
        self.assertFalse(before)
        r_dict, status_code = self.make_pipeline(build_executor)
        after = str(models.Pipeline.objects.all()) != '[]'
        self.assertTrue(after)

        self.assertIn('uuid', r_dict)
        self.assertNotIn('pk', r_dict)
        self.assertEqual(status_code, 201)

    def test_get_all_pipelines(self):
        """GET all pipeline instances."""
        pl_dict = []
        for idx in range(3):
            pl_dict.append(self.make_pipeline())
        response = self.api_client.get('/api/{}/pipeline/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']

        self.assertEqual(response.status_code, 200)
        for idx, pl in enumerate(pl_dict):
            self.assertIn(pl[0]['uuid'], objects[idx]['uuid'])

    def test_get_specific_pipeline(self):
        """GET a specific pipeline instance by its UUID."""
        r_dict0, status_code = self.make_pipeline()
        pipeline_id = r_dict0['uuid']
        response = self.api_client.get('/api/{}/pipeline/{}/'
                                       .format(self.version, pipeline_id),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(pipeline_id, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200)

    def test_put_method_not_allowed(self):
        """PUT to update an existing pipeline instance."""
        r_dict0, status_code = self.make_pipeline()
        pipeline_id = r_dict0['uuid']
        response = self.api_client.put('/api/{}/pipeline/{}/'
                                       .format(self.version, pipeline_id),
                                       data={}, format='json')
        self.assertIsNone(self.deserialize(response))
        self.assertEqual(response.status_code, 405)

    def test_delete_pipeline(self):
        """DELETE an existing pipeline instance."""
        r_dict0, status_code = self.make_pipeline()
        pipeline_id = r_dict0['uuid']

        self.assertTrue(models.Pipeline.objects.filter(uuid=pipeline_id)
                        .count() > 0)
        response = self.api_client.delete('/api/{}/pipeline/{}/'
                                          .format(self.version, pipeline_id),
                                          format='json')

        non_obj = models.Pipeline.objects.filter(uuid=pipeline_id)
        self.assertEqual(non_obj.count(), 0)
        self.assertEqual(response.status_code, 204)
