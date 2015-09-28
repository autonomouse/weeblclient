#! /usr/bin/env python3
import utils
import arrow

from tastypie.resources import ALL, ALL_WITH_RELATIONS
from freezegun import freeze_time
from django.db.utils import IntegrityError

from common_test_methods import ResourceTests
from oilserver import models
from exceptions import NonUserEditableError
from oilserver.api.resources import BuildResource, BuildStatusResource,\
    JobTypeResource


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


class EnvironmentResourceTest(ResourceTests):

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

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
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
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

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

    def test_post_create_environment(self):
        """POST to create a new environment instance."""
        uuid = utils.generate_uuid()
        data = {'name': utils.generate_random_string(),
                'uuid': uuid}
        r_dict, status_code = self.post_create_instance(
            'environment',
            data=data)
        new_obj = models.Environment.objects.filter(uuid=r_dict['uuid'])

        self.assertIn('uuid', r_dict)
        self.assertNotEqual(new_obj.count(), 0)
        self.assertEqual(status_code, 201)
        self.assertEqual(uuid, r_dict['uuid'])

    def test_post_create_environment_with_uuid(self):
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
        self.assertNotEqual(r_dict['name'], new_r_dict['name'],
                            msg="Name is not different in updated environment")
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

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

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(new_uuid, new_r_dict['uuid'],
                            msg="UUID should not have been updated!")
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
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

    def test_get_filter_by_uuid(self):
        r_dict0 = self.make_environment()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/environment/?uuid={}'
                                       .format(self.version, uuid))
        r_dict = self.deserialize(response)['objects'][0]
        returned_uuid = r_dict['uuid']
        self.assertEqual(uuid, returned_uuid)


class ServiceStatusResourceTests(ResourceTests):

    def test_get_method_is_allowed(self):
        """Validate that user can GET service_status model."""
        response =\
            self.api_client.get('/api/{}/service_status/'.format(self.version))
        r_dict = self.deserialize(response)

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

        for idx, bstat in enumerate(r_dict['objects']):
            self.assertNotIn('pk', bstat)
            self.assertIn('name', bstat)

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


class JenkinsResourceTests(ResourceTests):

    def setUp(self):
        super(JenkinsResourceTests, self).setUp()
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

        # Update status via PUT request (check-in):
        response2 = self.api_client.put(
            '/api/{}/jenkins/{}/'.format(self.version, returned_uuid),
            data={},
            format='json')
        r_dict2 = self.deserialize(response2)
        timestamp = r_dict2['service_status_updated_at']

        self.assertTrue(utils.uuid_check(returned_uuid),
                        "Did not return a UUID")
        self.assertNotIn("pk", r_dict2,
                         "A primary key was returned along with the check-in")
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

    def test_make_sure_service_statuses_are_obscured_upon_jenkins_get(self):
        """A get on jenkins should not reveal the pk for service status."""
        uuid, random_name = self.make_environment_and_jenkins()
        response1 = self.api_client.get(
            '/api/{}/jenkins/'.format(self.version), format='json')
        r_dict1 = self.deserialize(response1)

        first_object = r_dict1['objects'][0]
        value = first_object.get('service_status').rstrip('/').split('/')[-1]
        self.assertTrue(value in ['unknown', 'up', 'unstable', 'down'])

    def test_get_filter_by_uuid(self):
        uuid, random_name = self.make_environment_and_jenkins()
        response = self.api_client.get('/api/{}/jenkins/?uuid={}'
                                       .format(self.version, uuid))
        r_dict = self.deserialize(response)['objects'][0]
        returned_uuid = r_dict['uuid']
        self.assertEqual(uuid, returned_uuid)


class BuildExecutorResourceTests(ResourceTests):

    def test_post_create_build_executor(self):
        uuid, name = self.make_environment_and_jenkins()
        r_dict, status_code = self.make_build_executor(
            name=name, env_uuid=uuid)

        self.assertIn('uuid', r_dict)
        self.assertNotIn('pk', r_dict)
        self.assertEqual(r_dict['name'], name)
        self.assertNotEqual(r_dict['uuid'], uuid)
        self.assertEqual(status_code, 201, msg="Incorrect status code")

    def test_post_create_unnamed_build_executor(self):
        uuid, name = self.make_environment_and_jenkins()
        r_dict, status_code = self.make_build_executor(
            env_uuid=uuid)
        self.assertEqual(r_dict['name'], r_dict['uuid'])

    def test_get_all_build_executors(self):
        """GET all build_executor instances."""
        bex_dict = [self.make_build_executor() for _ in range(3)]
        response = self.api_client.get('/api/{}/build_executor/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
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
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_get_build_executor_uuid_from_name(self):
        r_dict0, status_code = self.make_build_executor()
        uuid_to_match = r_dict0.get('uuid')
        jenkins = r_dict0.get('jenkins')
        build_executor_name = r_dict0.get('name')
        response = self.api_client.get(
            '/api/{}/build_executor/?jenkins={}&name={}'
            .format(self.version, jenkins, build_executor_name))
        r_dict = self.deserialize(response)
        objects = r_dict['objects']
        self.assertTrue(uuid_to_match, objects[0].get('uuid'))

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
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        after = models.BuildExecutor.objects.filter(name=new_name).exists()
        self.assertTrue(after)
        new_r_dict = self.deserialize(response)
        self.assertNotEqual(r_dict['name'], new_r_dict['name'],
                            msg="Name is not different in updated environment")

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

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(uuid2, new_r_dict['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_post_cannot_make_two_build_executors_with_same_name(self):
        shared_uuid, env_name1 = self.make_environment_and_jenkins()
        shared_name = utils.generate_random_string()
        r_dict1, status_code = self.make_build_executor(
            name=shared_name, env_uuid=shared_uuid)
        with self.assertRaises(IntegrityError):
            r_dict2, status_code = self.make_build_executor(
                name=shared_name, env_uuid=shared_uuid)

    def test_build_executors_with_same_name_ok_if_different_jenkins(self):
        uuid1, env_name1 = self.make_environment_and_jenkins()
        uuid2, env_name2 = self.make_environment_and_jenkins()
        shared_name = utils.generate_random_string()
        try:
            r_dict1, status_code = self.make_build_executor(
                name=shared_name, env_uuid=uuid1)
            r_dict2, status_code = self.make_build_executor(
                name=shared_name, env_uuid=uuid2)
            created_two_build_executors = True
        except:
            created_two_build_executors = False
        msg = "Failed to create multiple build executors with the same name "
        msg += "on different jenkins"
        self.assertTrue(created_two_build_executors, msg=msg)
        self.assertEqual(r_dict1.get('name'), r_dict2.get('name'))
        self.assertNotEqual(r_dict1.get('jenkins'), r_dict2.get('jenkins'))

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

    def test_get_filter_by_uuid(self):
        r_dict0, status_code = self.make_build_executor()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/build_executor/?uuid={}'
                                       .format(self.version, uuid))
        r_dict = self.deserialize(response)['objects'][0]
        returned_uuid = r_dict['uuid']
        self.assertEqual(uuid, returned_uuid)

    def test_get_filter_by_name(self):
        r_dict0, status_code = self.make_build_executor()
        name = r_dict0['name']
        response = self.api_client.get('/api/{}/build_executor/?name={}'
                                       .format(self.version, name))
        r_dict = self.deserialize(response)['objects'][0]
        returned_name = r_dict['name']
        self.assertEqual(name, returned_name)

    def test_get_filter_by_uuid_and_name(self):
        r_dict0, status_code = self.make_build_executor()
        uuid = r_dict0['uuid']
        name = r_dict0['name']
        response = self.api_client.get(
            '/api/{}/build_executor/?uuid={}&name={}'
            .format(self.version, uuid, name))
        r_dict = self.deserialize(response)['objects'][0]
        returned_uuid = r_dict['uuid']
        returned_name = r_dict['name']
        self.assertEqual(uuid, returned_uuid)
        self.assertEqual(name, returned_name)


class PipelineResourceTests(ResourceTests):

    def test_post_create_pipeline(self):
        build_executor = self.make_build_executor()[0]['uuid']
        before = str(models.Pipeline.objects.all()) != '[]'
        self.assertFalse(before)
        r_dict, status_code = self.make_pipeline(build_executor)
        after = str(models.Pipeline.objects.all()) != '[]'
        self.assertTrue(after)

        self.assertIn('uuid', r_dict)
        self.assertNotIn('pk', r_dict)
        self.assertEqual(status_code, 201, msg="Incorrect status code")

    def test_get_all_pipelines(self):
        """GET all pipeline instances."""
        pl_dict = []
        for _ in range(3):
            pl_dict.append(self.make_pipeline())
        response = self.api_client.get('/api/{}/pipeline/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
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
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_get_specific_pipeline_matches_uuid(self):
        """GET a specific pipeline instance by its UUID."""
        pl = utils.generate_uuid()
        r_dict0, status_code = self.make_pipeline(pipeline=pl)
        pipeline_id = r_dict0['uuid']
        response = self.api_client.get('/api/{}/pipeline/{}/'
                                       .format(self.version, pipeline_id),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(pipeline_id, pl,
                         msg="Returned pipeline does not match given pipeline")
        self.assertEqual(pipeline_id, r_dict1['uuid'],
                         msg="Returned pipeline does not match url pipeline")
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_put_update_existing_pipeline(self):
        """PUT to update an existing pipeline instance."""
        r_dict0, status_code = self.make_pipeline()
        pipeline_id = r_dict0['uuid']

        before = self.api_client.get('/api/{}/pipeline/{}/'
                                     .format(self.version, pipeline_id),
                                     format='json')
        r_dict1 = self.deserialize(before)
        self.assertEqual(pipeline_id, r_dict1['uuid'])
        self.assertEqual(None, r_dict1['completed_at'],
                         msg="completed_at already set on new pipeline")
        self.assertEqual(before.status_code, 200,
                         msg="Incorrect status code")

        new_completed_at = utils.time_now()
        data = {'completed_at': new_completed_at}
        response = self.api_client.put('/api/{}/pipeline/{}/'
                                       .format(self.version, pipeline_id),
                                       data=data)
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        pipeline = models.Pipeline.objects.get(uuid=pipeline_id)
        self.assertEqual(
            new_completed_at, pipeline.completed_at,
            msg="completed_at was not updated.")

    def test_put_cannot_update_existing_pipeline_uuid(self):
        """PUT to update an existing pipeline instance."""
        r_dict, status_code = self.make_pipeline()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        data = {'uuid': uuid2}
        before = models.Pipeline.objects.filter(uuid=uuid2).exists()
        self.assertFalse(before)

        response = self.api_client.put('/api/{}/pipeline/{}/'
                                       .format(self.version, uuid), data=data)

        after = models.Pipeline.objects.filter(uuid=uuid2).exists()
        self.assertFalse(after, msg="pipeline UUID has been altered!")
        new_r_dict = self.deserialize(response)

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(uuid2, new_r_dict['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

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

    def test_get_filter_by_uuid(self):
        r_dict0, status_code = self.make_pipeline()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/pipeline/?uuid={}'
                                       .format(self.version, uuid))
        r_dict = self.deserialize(response)['objects'][0]
        returned_uuid = r_dict['uuid']
        self.assertEqual(uuid, returned_uuid)


class BuildStatusResourceTests(ResourceTests):

    def test_get_method_is_allowed(self):
        """Validate that user can GET build_status model."""
        response =\
            self.api_client.get('/api/{}/build_status/'.format(self.version))
        r_dict = self.deserialize(response)

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

        for idx, bstat in enumerate(r_dict['objects']):
            self.assertNotIn('pk', bstat)
            self.assertIn('name', bstat)

    def test_post_method_not_allowed(self):
        """Validate that user cannot POST build_status model."""
        response = self.api_client.post('/api/{}/build_status/'
                                        .format(self.version))
        r_dict = self.deserialize(response)

        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_put_method_not_allowed(self):
        """Validate that user cannot PUT build_status model."""
        response = self.api_client.put('/api/{}/build_status/'
                                       .format(self.version))
        r_dict = self.deserialize(response)

        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_delete_method_not_allowed(self):
        """Validate that user cannot DELETE a specific build_status model."""
        response = self.api_client.delete('/api/{}/build_status/0/'
                                          .format(self.version))
        r_dict = self.deserialize(response)

        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_resource_filtering(self):
        expected_filtering = {
            'name': ALL,
        }
        self.assertEqual(
            expected_filtering,
            BuildStatusResource._meta.filtering)


class JobTypeResourceTests(ResourceTests):

    def test_get_method_is_allowed(self):
        """Validate that user can GET job_type model."""
        response =\
            self.api_client.get('/api/{}/job_type/'.format(self.version))
        r_dict = self.deserialize(response)

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

        for idx, bstat in enumerate(r_dict['objects']):
            self.assertNotIn('pk', bstat)
            self.assertIn('name', bstat)

    def test_post_method_not_allowed(self):
        """Validate that user cannot POST job_type model."""
        response = self.api_client.post('/api/{}/job_type/'
                                        .format(self.version))
        r_dict = self.deserialize(response)

        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_put_method_not_allowed(self):
        """Validate that user cannot PUT job_type model."""
        response = self.api_client.put('/api/{}/job_type/'
                                       .format(self.version))
        r_dict = self.deserialize(response)

        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_delete_method_not_allowed(self):
        """Validate that user cannot DELETE a specific job_type model."""
        response = self.api_client.delete('/api/{}/job_type/0/'
                                          .format(self.version))
        r_dict = self.deserialize(response)

        self.assertIsNone(r_dict)
        self.assertEqual(response.status_code, 405)

    def test_resource_filtering(self):
        expected_filtering = {
            'name': ALL,
        }
        self.assertEqual(
            expected_filtering,
            JobTypeResource._meta.filtering)


class BuildResourceTests(ResourceTests):

    def setUp(self):
        super(BuildResourceTests, self).setUp()
        self.pipeline_id = self.make_pipeline()[0]['uuid']

    def test_post_create_build_without_timestamps(self):
        build_id = utils.generate_random_number_as_string()
        build_status = "success"
        job_type = "pipeline_deploy"

        data = {'build_id': str(build_id),
                'pipeline': self.pipeline_id,
                'build_status': build_status,
                'job_type': job_type}

        r_dict, status_code = self.post_create_instance(
            'build', data=data)

        recently_analysed = utils.time_difference_less_than_x_mins(
            r_dict['build_analysed_at'], 1)
        self.assertTrue(recently_analysed,
                        msg="Build_analysed_at was over 1 minute ago")
        self.assertIn('uuid', r_dict, msg="UUID not in response")
        self.assertEqual(build_id, r_dict['build_id'],
                         msg="Incorrect build id")
        self.assertIn(build_status, r_dict['build_status'],
                      msg="Incorrect build status")
        self.assertIn(job_type, r_dict['job_type'], msg="Incorrect job type")
        self.assertNotIn('pk', r_dict,
                         msg="Primary key is showing up in response")
        self.assertEqual(status_code, 201, msg="Incorrect status code")
        self.assertIn(job_type, r_dict['artifact_location'].split('/'))
        self.assertIn(str(build_id), r_dict['artifact_location'].split('/'))
        self.assertIn('artifact', r_dict['artifact_location'].split('/'))

    def test_post_create_build_with_timestamps(self):
        build_id = utils.generate_random_number_as_string()
        build_status = "success"
        job_type = "pipeline_deploy"
        with freeze_time("Jan 1 2000 00:00:00"):
            timestamp0 = utils.time_now()
        with freeze_time("Jan 1 2000 00:00:05"):
            timestamp1 = utils.time_now()

        data = {'build_id': str(build_id),
                'build_started_at': timestamp0,
                'build_finished_at': timestamp1,
                'pipeline': self.pipeline_id,
                'build_status': build_status,
                'job_type': job_type}

        r_dict, status_code = self.post_create_instance(
            'build', data=data)
        recently_analysed = utils.time_difference_less_than_x_mins(
            r_dict['build_analysed_at'], 1)
        self.assertTrue(recently_analysed,
                        msg="Build_analysed_at was over 1 minute ago")

        self.assertEqual(arrow.get(r_dict['build_started_at']),
                         arrow.get(timestamp0))
        self.assertEqual(arrow.get(r_dict['build_finished_at']),
                         arrow.get(timestamp1))

        self.assertIn('uuid', r_dict, msg="UUID not in response")
        self.assertEqual(build_id, r_dict['build_id'],
                         msg="Incorrect build id")
        self.assertIn(build_status, r_dict['build_status'],
                      msg="Incorrect build status")
        self.assertIn(job_type, r_dict['job_type'], msg="Incorrect job type")
        self.assertNotIn('pk', r_dict,
                         msg="Primary key is showing up in response")
        self.assertEqual(status_code, 201, msg="Incorrect status code")

    def test_put_update_existing_builds(self):
        """PUT to update an existing build instance."""
        r_dict, status_code = self.make_build()
        original_build_id = r_dict['build_id']
        before = models.Build.objects.filter(
            build_id=original_build_id).exists()
        self.assertTrue(before)
        updated_build_id = '12345'
        data = {'build_id': updated_build_id}
        response = self.api_client.put(
            '/api/{}/build/{}/'.format(self.version, r_dict['uuid']),
            data=data)
        after_orig = models.Build.objects.filter(
            build_id=original_build_id).exists()
        self.assertFalse(after_orig)
        after = models.Build.objects.filter(
            build_id=updated_build_id).exists()
        self.assertTrue(after)

        new_r_dict = self.deserialize(response)
        self.assertNotEqual(original_build_id, new_r_dict['build_id'],
                            msg="Build id in response different to original")
        self.assertEqual(updated_build_id, new_r_dict['build_id'],
                         msg="Build id has not been updated")
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_put_cannot_update_existing_builds_uuid(self):
        """PUT to update an existing build instance."""
        r_dict, status_code = self.make_build()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        data = {'uuid': uuid2}
        before = models.Build.objects.filter(uuid=uuid2).exists()
        self.assertFalse(before)

        response = self.api_client.put('/api/{}/build/{}/'
                                       .format(self.version, uuid), data=data)

        after = models.Build.objects.filter(uuid=uuid2).exists()
        self.assertFalse(after, msg="build_executor UUID has been altered!")
        new_r_dict = self.deserialize(response)

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(uuid2, new_r_dict['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_get_all_builds(self):
        """GET all build instances."""
        build_dict = []
        for _ in range(3):
            build_dict.append(self.make_build())
        response = self.api_client.get('/api/{}/build/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        for idx, pl in enumerate(build_dict):
            self.assertIn(pl[0]['uuid'], objects[idx]['uuid'])

    def test_get_specific_build(self):
        """GET a specific build instance by its UUID."""
        r_dict0, status_code = self.make_build()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/build/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_delete_build(self):
        """DELETE an existing build instance."""
        r_dict0, status_code = self.make_build()
        uuid = r_dict0['uuid']

        self.assertTrue(models.Build.objects.filter(uuid=uuid)
                        .count() > 0)
        response = self.api_client.delete('/api/{}/build/{}/'
                                          .format(self.version, uuid),
                                          format='json')

        non_obj = models.Build.objects.filter(uuid=uuid)
        self.assertEqual(non_obj.count(), 0, msg="Build not deleted")
        self.assertEqual(response.status_code, 204,
                         msg="Incorrect status code")

    def test_make_sure_build_statuses_are_obscured_upon_build_get(self):
        """A get on build should not reveal the pk for build_status."""
        r_dict0, status_code = self.make_build()
        response = self.api_client.get(
            '/api/{}/build/'.format(self.version), format='json')
        r_dict1 = self.deserialize(response)

        first_object = r_dict1['objects'][0]
        value = first_object.get('build_status').rstrip('/').split('/')[-1]
        self.assertTrue(value in ['unknown', 'success', 'failure', 'aborted'])

    def test_resource_filtering(self):
        expected_filtering = {
            'uuid': ALL,
            'build_id': ALL,
            'job_type': ALL_WITH_RELATIONS,
            'pipeline': ALL_WITH_RELATIONS,
            'build_status': ALL_WITH_RELATIONS
        }
        self.assertEqual(
            expected_filtering,
            BuildResource._meta.filtering)


class TargetFileGlobResourceTests(ResourceTests):

    def test_get_method_is_allowed(self):
        """Validate that user can GET target_file_glob model."""
        response = self.api_client.get(
            '/api/{}/target_file_glob/'.format(self.version))
        r_dict = self.deserialize(response)

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

        for idx, globs in enumerate(r_dict['objects']):
            self.assertNotIn('pk', globs)
            self.assertIn('name', globs)

    def test_post_create_target_file_glob(self):
        before = str(models.TargetFileGlob.objects.all()) != '[]'
        self.assertFalse(before)
        job_types = 'pipeline_deploy'
        r_dict, status_code = self.make_target_file_glob(job_types=job_types)
        after = str(models.TargetFileGlob.objects.all()) != '[]'
        self.assertTrue(after)

        self.assertIn(job_types, r_dict['job_types'])
        self.assertIn('glob_pattern', r_dict)
        self.assertNotIn('pk', r_dict)
        self.assertEqual(status_code, 201, msg="Incorrect status code")

    def test_post_create_target_file_glob_without_job_type(self):
        before = str(models.TargetFileGlob.objects.all()) != '[]'
        self.assertFalse(before)
        r_dict, status_code = self.make_target_file_glob()
        after = str(models.TargetFileGlob.objects.all()) != '[]'
        self.assertTrue(after)

        self.assertIn('glob_pattern', r_dict)
        self.assertNotIn('pk', r_dict)
        self.assertEqual(status_code, 201, msg="Incorrect status code")

    def test_get_all_target_file_globs(self):
        """GET all target_file_glob instances."""
        pl_dict = []
        for _ in range(3):
            pl_dict.append(self.make_target_file_glob())
        response = self.api_client.get('/api/{}/target_file_glob/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']

        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        for idx, pl in enumerate(pl_dict):
            self.assertIn(pl[0]['glob_pattern'], objects[idx]['glob_pattern'])

    def test_get_specific_target_file_glob(self):
        """GET a specific target_file_glob instance by its UUID."""
        r_dict0, status_code = self.make_target_file_glob()
        target_file_glob_name = r_dict0['glob_pattern']
        response = self.api_client.get(
            '/api/{}/target_file_glob/{}/'.format(
                self.version, target_file_glob_name), format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(target_file_glob_name, r_dict1['glob_pattern'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_put_update_existing_target_file_globs(self):
        """PUT to update an existing target_file_glob instance."""
        r_dict, status_code = self.make_target_file_glob()
        original_glob_pattern = r_dict['glob_pattern']
        before = models.TargetFileGlob.objects.filter(
            glob_pattern=original_glob_pattern).exists()
        self.assertTrue(before, msg="Glob pattern already exists")
        updated_glob_pattern = 'NewNameWithADot.txt'
        data = {'glob_pattern': updated_glob_pattern}
        response = self.api_client.put('/api/{}/target_file_glob/{}/'.format(
            self.version, r_dict['glob_pattern']), data=data)
        after_orig = models.TargetFileGlob.objects.filter(
            glob_pattern=original_glob_pattern).exists()
        self.assertFalse(after_orig)
        after = models.TargetFileGlob.objects.filter(
            glob_pattern=updated_glob_pattern).exists()
        self.assertTrue(after, msg="Glob pattern has not been updated")

        new_r_dict = self.deserialize(response)
        self.assertNotEqual(original_glob_pattern, new_r_dict['glob_pattern'],
                            msg="Response glob pattern different to original")
        self.assertEqual(updated_glob_pattern, new_r_dict['glob_pattern'],
                         msg="Glob pattern has not been updated")
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_delete_target_file_glob(self):
        """DELETE an existing target_file_glob instance."""
        r_dict0, status_code = self.make_target_file_glob()
        target_file_glob_name = r_dict0['glob_pattern']

        self.assertTrue(models.TargetFileGlob.objects.filter(
            glob_pattern=target_file_glob_name).count() > 0)
        response = self.api_client.delete(
            '/api/{}/target_file_glob/{}/'.format(
                self.version, target_file_glob_name), format='json')

        non_obj = models.TargetFileGlob.objects.filter(
            glob_pattern=target_file_glob_name)
        self.assertEqual(non_obj.count(), 0)
        self.assertEqual(response.status_code, 204)

    def test_get_filter_by_glob_pattern(self):
        r_dict0, status_code = self.make_target_file_glob()
        glob_pattern = r_dict0['glob_pattern']
        response = self.api_client.get(
            '/api/{}/target_file_glob/?glob_pattern={}'
            .format(self.version, glob_pattern))
        r_dict = self.deserialize(response)['objects'][0]
        returned_glob_pattern = r_dict['glob_pattern']
        self.assertEqual(glob_pattern, returned_glob_pattern)


class KnownBugRegexResourceTests(ResourceTests):

    def test_post_create_known_bug_regex_makes_new_target_file_globs(self):
        new_files = [utils.generate_random_string() for _ in range(3)]

        # Target files shouldn't exist before create_known_bug_regex called:
        target_file_globs_before = [obj.file_name for obj in
                                    models.TargetFileGlob.objects.all()]
        for new_file in new_files:
            self.assertNotIn(new_file, target_file_globs_before)

        # Create KnownBugRegex
        data = {"target_file_globs": new_files,
                "regex": utils.generate_random_string()}
        r_dict, status_code = self.post_create_instance(
            'known_bug_regex', data=data)

        # Target files should exist after create known_bug_regex called:
        target_file_globs_after = [tfglob.glob_pattern for tfglob in
                                   models.TargetFileGlob.objects.all()]
        for new_file in new_files:
            self.assertIn(new_file, target_file_globs_after)

    def test_post_create_known_bug_regex_makes_new_bug(self):
        new_bug = utils.generate_random_string()

        # Bug shouldn't exist before create_known_bug_regex call made:
        bugs_before = [obj.uuid for obj in models.Bug.objects.all()]
        self.assertNotIn(new_bug, bugs_before)

        # Create KnownBugRegex
        data = {"bug": new_bug,
                "target_file_globs": utils.generate_random_string(),
                "regex": utils.generate_random_string()}
        r_dict, status_code = self.post_create_instance(
            'known_bug_regex', data=data)

        # Bug should exist after create known_bug_regex call is made:
        bugs_after = [obj.uuid for obj in models.Bug.objects.all()]
        self.assertIn(new_bug, bugs_after)

    def test_post_create_known_bug_regex_logs_time_correctly(self):
        data = {"target_file_globs": "console.txt",
                "regex": "abcd"}

        with freeze_time("Jan 1 2000 00:00:00"):
            timestamp = utils.time_now()
            r_dict, status_code = self.post_create_instance(
                'known_bug_regex', data=data)

        ts1 = utils.timestamp_as_string(timestamp)
        ts2 = utils.timestamp_as_string(r_dict['created_at'])
        ts3 = utils.timestamp_as_string(r_dict['updated_at'])

        self.assertEqual(ts1, ts2, msg="Incorrect creation datetime")
        self.assertEqual(ts1, ts3, msg="Incorrect last_edited datetime")
        self.assertEqual(status_code, 201, msg="Incorrect status code")

    def test_post_create_known_bug_regex_with_no_target_file_globs(self):
        data1 = {"regex": utils.generate_random_string()}
        r_dict1, statuscode1 = self.post_create_instance(
            'known_bug_regex', data=data1)
        data2 = {"target_file_globs": [],
                 "regex": utils.generate_random_string()}
        r_dict2, statuscode2 = self.post_create_instance(
            'known_bug_regex', data=data2)
        self.assertEqual(statuscode1, 201, msg="Incorrect status code")
        self.assertEqual(statuscode2, 201, msg="Incorrect status code")
        self.assertEqual(r_dict1.get('target_file_globs'), [])
        self.assertEqual(r_dict2.get('target_file_globs'), [])

    def test_post_create_known_bug_regex_with_one_target_file(self):
        single_file = "{}.txt".format(utils.generate_random_string())
        data = {"target_file_globs": single_file,
                "regex": utils.generate_random_string()}
        r_dict, status_code = self.post_create_instance(
            'known_bug_regex', data=data)
        self.assertEqual(status_code, 201, msg="Incorrect status code")
        self.assertEqual(r_dict['target_file_globs'], [single_file],
                         msg="Incorrect target file returned")

    def test_post_create_known_bug_regex_with_two_target_files(self):
        new_files = [utils.generate_random_string() for _ in range(2)]
        data = {"target_file_globs": new_files,
                "regex": utils.generate_random_string()}
        r_dict, status_code = self.post_create_instance(
            'known_bug_regex', data=data)
        self.assertEqual(status_code, 201, msg="Incorrect status code")
        self.assertEqual(r_dict['target_file_globs'], new_files,
                         msg="Incorrect target files returned")

    def test_post_cannot_upload_non_unique_known_bug_regex(self):
        regex = utils.generate_random_string()
        data1 = {"regex": regex}
        data2 = {"target_file_globs": utils.generate_random_string(),
                 "regex": regex}
        self.post_create_instance('known_bug_regex', data=data1)
        with self.assertRaises(IntegrityError):
            self.post_create_instance('known_bug_regex', data=data2)

    def test_put_update_existing_known_bug_regexs(self):
        """PUT to update an existing known_bug_regex instance."""
        r_dict0, status_code = self.make_known_bug_regex()
        uuid = r_dict0['uuid']
        original_regex = r_dict0['regex']
        before = models.KnownBugRegex.objects.filter(
            regex=original_regex).exists()
        self.assertTrue(before)
        time_before = models.KnownBugRegex.objects.get(
            uuid=uuid).updated_at
        updated_regex = utils.generate_random_string()
        data = {'regex': updated_regex}
        response = self.api_client.put(
            '/api/{}/known_bug_regex/{}/'.format(
                self.version, r_dict0['uuid']), data=data)
        r_dict1 = self.deserialize(response)
        self.assertFalse(models.KnownBugRegex.objects
                         .filter(regex=original_regex).exists(),
                         msg="regex not updated")
        after = models.KnownBugRegex.objects.filter(
            regex=updated_regex).exists()
        time_after = models.KnownBugRegex.objects.get(
            uuid=uuid).updated_at
        self.assertTrue(after, msg="regex incorrectly updated")
        self.assertNotIn('pk', r_dict1, msg="Primary key in response!")
        self.assertNotEqual(
            time_before, time_after,
            msg="Updated_at should have been updated!")

    def test_put_update_bug_in_known_bug_regexs(self):
        """PUT to update the bug in an existing known_bug_regex instance."""
        bug_uuid = utils.generate_random_string()
        r_dict0, status_code = self.make_known_bug_regex(bug=bug_uuid)
        before = False
        for obj in models.KnownBugRegex.objects.all():
            if obj.bug is not None:
                if bug_uuid == obj.bug.uuid:
                    before = True
                    break
        self.assertTrue(before, msg="Bug UUID was not initially set!")
        updated_bug_uuid = utils.generate_random_string()
        data = {'bug': updated_bug_uuid}
        self.api_client.put('/api/{}/known_bug_regex/{}/'.format(
            self.version, r_dict0['uuid']), data=data)
        after = False
        for obj in models.KnownBugRegex.objects.all():
            if bug_uuid == obj.bug.uuid:
                after = True
                break
        self.assertTrue(after, msg="Bug not updated")

    def test_put_cannot_update_updated_at_manually(self):
        """PUT to update an existing pattern instance."""
        r_dict, status_code = self.make_known_bug_regex()
        uuid = r_dict['uuid']
        time_before =\
            models.KnownBugRegex.objects.get(uuid=uuid).updated_at
        updated_at = utils.generate_random_date()
        data = {'updated_at': updated_at}

        with self.assertRaises(NonUserEditableError):
            self.api_client.put('/api/{}/known_bug_regex/{}/'
                                .format(self.version, uuid), data=data)
        time_after =\
            models.KnownBugRegex.objects.get(uuid=uuid).updated_at
        self.assertEqual(
            time_before, time_after,
            msg="updated_at should not have been updated!")

    def test_put_cannot_update_created_at(self):
        r_dict, status_code = self.make_known_bug_regex()
        uuid = r_dict['uuid']
        time_before = models.KnownBugRegex.objects.get(
            uuid=uuid).created_at
        created_at = utils.generate_random_date()
        data = {'created_at': created_at}
        with self.assertRaises(NonUserEditableError):
            self.api_client.put('/api/{}/known_bug_regex/{}/'.format(
                self.version, uuid), data=data)
        time_after = models.KnownBugRegex.objects.get(
            uuid=uuid).created_at
        self.assertEqual(
            time_before, time_after,
            msg="created_at should not have been updated!")

    def test_put_cannot_update_existing_known_bug_regexs_uuid(self):
        """PUT to update an existing known_bug_regex instance."""
        r_dict, status_code = self.make_known_bug_regex()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        data = {'uuid': uuid2}
        self.assertFalse(
            models.KnownBugRegex.objects.filter(uuid=uuid2).exists())

        response = self.api_client.put('/api/{}/known_bug_regex/{}/'
                                       .format(self.version, uuid), data=data)

        self.assertFalse(
            models.KnownBugRegex.objects.filter(uuid=uuid2).exists(),
            msg="KnownBugRegex UUID has been altered!")
        new_r_dict = self.deserialize(response)

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(uuid2, new_r_dict['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_get_all_known_bug_regexs(self):
        """GET all known_bug_regex instances."""
        regex_dict = []
        for _ in range(3):
            regex_dict.append(self.make_known_bug_regex())
        response = self.api_client.get('/api/{}/known_bug_regex/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        uuids = [obj['uuid'] for obj in objects]
        for idx, ptrn in enumerate(regex_dict):
            self.assertIn(ptrn[0]['uuid'], uuids)

    def test_get_specific_known_bug_regex(self):
        """GET a specific known_bug_regex instance by its UUID."""
        r_dict0, status_code = self.make_known_bug_regex()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/known_bug_regex/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_delete_known_bug_regex(self):
        """DELETE an existing known_bug_regex instance."""
        r_dict0, status_code = self.make_known_bug_regex()
        uuid = r_dict0['uuid']

        self.assertTrue(models.KnownBugRegex.objects.filter(uuid=uuid)
                        .count() > 0)
        response = self.api_client.delete('/api/{}/known_bug_regex/{}/'
                                          .format(self.version, uuid),
                                          format='json')

        non_obj = models.KnownBugRegex.objects.filter(uuid=uuid)
        self.assertEqual(non_obj.count(), 0,
                         msg="KnownBugRegex not deleted")
        self.assertEqual(response.status_code, 204,
                         msg="Incorrect status code")

    def test_get_filter_by_uuid(self):
        r_dict0, status_code = self.make_known_bug_regex()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/known_bug_regex/?uuid={}'
                                       .format(self.version, uuid))
        r_dict = self.deserialize(response)['objects'][0]
        returned_uuid = r_dict['uuid']
        self.assertEqual(uuid, returned_uuid)

    def test_get_filter_by_regex(self):
        r_dict0, status_code = self.make_known_bug_regex()
        regex = r_dict0['regex']
        response = self.api_client.get('/api/{}/known_bug_regex/?regex={}'
                                       .format(self.version, regex))
        r_dict = self.deserialize(response)['objects'][0]
        returned_regex = r_dict['regex']
        self.assertEqual(regex, returned_regex)

    def test_get_filter_by_regex_and_uuid(self):
        r_dict0, status_code = self.make_known_bug_regex()
        uuid = r_dict0['uuid']
        regex = r_dict0['regex']
        response = self.api_client.get(
            '/api/{}/known_bug_regex/?uuid={}&regex={}'
            .format(self.version, uuid, regex))
        r_dict = self.deserialize(response)['objects'][0]
        returned_uuid = r_dict['uuid']
        returned_regex = r_dict['regex']
        self.assertEqual(uuid, returned_uuid)
        self.assertEqual(regex, returned_regex)


class BugResourceTests(ResourceTests):

    def setUp(self):
        super(BugResourceTests, self).setUp()

    def test_post_create_bug_logs_time_correctly(self):
        with freeze_time("Jan 1 2000 00:00:00"):
            r_dict, status_code = self.make_bug()
            timestamp = utils.time_now()

        ts1 = utils.timestamp_as_string(timestamp)
        ts2 = utils.timestamp_as_string(r_dict['created_at'])
        ts3 = utils.timestamp_as_string(r_dict['updated_at'])

        self.assertEqual(ts1, ts2, msg="Incorrect creation datetime")
        self.assertEqual(ts1, ts3, msg="Incorrect last_edited datetime")
        self.assertEqual(status_code, 201, msg="Incorrect status code")

    def test_post_create_bug_with_only_summary_in_data(self):
        data = {'summary': utils.generate_random_string()}
        r_dict, statuscode = self.post_create_instance(
            'bug', data=data)
        self.assertEqual(statuscode, 201, msg="Incorrect status code")
        self.assertEqual(r_dict.get('description'), None)
        self.assertNotEqual(r_dict.get('uuid'), None)

    def test_put_cannot_update_existing_bug_uuid(self):
        """PUT to update an existing bug instance."""
        r_dict, status_code = self.make_bug()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        data = {'uuid': uuid2}
        before = models.Bug.objects.filter(uuid=uuid2).exists()
        self.assertFalse(before)

        response = self.api_client.put('/api/{}/bug/{}/'.format(
            self.version, uuid), data=data)

        after = models.BuildExecutor.objects.filter(uuid=uuid2).exists()
        self.assertFalse(after, msg="Bug UUID has been altered!")
        new_r_dict = self.deserialize(response)

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(uuid2, new_r_dict['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_put_update_existing_bugs(self):
        """PUT to update an existing bug instance."""
        r_dict0, status_code = self.make_bug()
        original_summary = r_dict0['summary']
        before = models.Bug.objects.filter(
            summary=original_summary).exists()
        self.assertTrue(before)
        time_before = models.Bug.objects.get(
            summary=original_summary).updated_at
        updated_summary = utils.generate_random_string()
        data = {'summary': updated_summary}
        response = self.api_client.put(
            '/api/{}/bug/{}/'.format(self.version, r_dict0['summary']),
            data=data)
        r_dict1 = self.deserialize(response)
        self.assertTrue(models.Bug.objects.filter(
            summary=original_summary).exists(), msg="UUID incorrectly updated")
        instance = models.Bug.objects.filter(summary=updated_summary)
        after = instance.exists()
        self.assertTrue(after, msg="UUID incorrectly updated")
        time_after = instance[0].updated_at
        self.assertNotIn('pk', r_dict1, msg="Primary key in response!")
        self.assertNotEqual(
            time_before, time_after,
            msg="Updated_at should have been updated!")

    def test_put_cannot_update_updated_at_manually(self):
        """PUT to update an existing pattern instance."""
        r_dict, status_code = self.make_bug()
        uuid = r_dict['uuid']
        time_before =\
            models.Bug.objects.get(uuid=uuid).updated_at
        updated_at = utils.generate_random_date()
        data = {'updated_at': updated_at}

        with self.assertRaises(NonUserEditableError):
            self.api_client.put('/api/{}/bug/{}/'
                                .format(self.version, uuid), data=data)
        time_after =\
            models.Bug.objects.get(uuid=uuid).updated_at
        self.assertEqual(
            time_before, time_after,
            msg="updated_at should not have been updated!")

    def test_put_cannot_update_created_at(self):
        r_dict, status_code = self.make_bug()
        uuid = r_dict['uuid']
        time_before = models.Bug.objects.get(
            uuid=uuid).created_at
        created_at = utils.generate_random_date()
        data = {'created_at': created_at}
        with self.assertRaises(NonUserEditableError):
            self.api_client.put('/api/{}/bug/{}/'.format(
                self.version, uuid), data=data)
        time_after = models.Bug.objects.get(
            uuid=uuid).created_at
        self.assertEqual(
            time_before, time_after,
            msg="created_at should not have been updated!")

    def test_put_cannot_update_existing_bugs_uuid(self):
        """PUT to update an existing bug instance."""
        r_dict, status_code = self.make_bug()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        data = {'uuid': uuid2}
        before = models.Bug.objects.filter(uuid=uuid2).exists()
        self.assertFalse(before)

        response = self.api_client.put('/api/{}/bug/{}/'.format(
            self.version, uuid), data=data)

        after = models.Bug.objects.filter(uuid=uuid2).exists()
        self.assertFalse(after, msg="Bug UUID has been altered!")

        new_r_dict = self.deserialize(response)

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(uuid2, new_r_dict['uuid'],
                            msg="UUID should not have been updated!")
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_get_all_bugs(self):
        """GET all bug instances."""
        bug_dict = []
        for _ in range(3):
            bug_dict.append(self.make_bug())
        response = self.api_client.get('/api/{}/bug/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        uuids = [obj['uuid'] for obj in objects]
        for idx, ptrn in enumerate(bug_dict):
            self.assertIn(ptrn[0]['uuid'], uuids)

    def test_get_specific_bug(self):
        """GET a specific bug instance by its UUID."""
        r_dict0, status_code = self.make_bug()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/bug/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_delete_bug(self):
        """DELETE an existing bug instance."""
        r_dict0, status_code = self.make_bug()
        uuid = r_dict0['uuid']

        self.assertTrue(models.Bug.objects.filter(uuid=uuid)
                        .count() > 0)
        response = self.api_client.delete('/api/{}/bug/{}/'
                                          .format(self.version, uuid),
                                          format='json')

        non_obj = models.Bug.objects.filter(uuid=uuid)
        self.assertEqual(non_obj.count(), 0, msg="Bug not deleted")
        self.assertEqual(response.status_code, 204,
                         msg="Incorrect status code")


class BugTrackerBugResourceTests(ResourceTests):

    def setUp(self):
        super(BugTrackerBugResourceTests, self).setUp()

    def test_post_create_bug_tracker_bug_logs_time_correctly(self):
        with freeze_time("Jan 1 2000 00:00:00"):
            r_dict, status_code = self.make_bug_tracker_bug()
            timestamp = utils.time_now()

        ts1 = utils.timestamp_as_string(timestamp)
        ts2 = utils.timestamp_as_string(r_dict['created_at'])
        ts3 = utils.timestamp_as_string(r_dict['updated_at'])

        self.assertEqual(ts1, ts2, msg="Incorrect creation datetime")
        self.assertEqual(ts1, ts3, msg="Incorrect last_edited datetime")
        self.assertEqual(status_code, 201, msg="Incorrect status code")

    def test_post_create_bug_tracker_bug(self):
        bug_id = utils.generate_random_number_as_string()
        data = {"bug_id": bug_id}
        r_dict, statuscode = self.post_create_instance(
            'bug_tracker_bug', data=data)
        self.assertEqual(statuscode, 201, msg="Incorrect status code")
        self.assertEqual(r_dict['bug_id'], bug_id)

    def test_post_cannot_upload_non_unique_bug_id(self):
        bug_id = utils.generate_random_number_as_string()
        data1 = {"bug_id": bug_id}
        data2 = {"bug_id": bug_id,
                 "summary": utils.generate_random_string()}
        self.post_create_instance('bug_tracker_bug', data=data1)
        with self.assertRaises(IntegrityError):
            self.post_create_instance('bug_tracker_bug', data=data2)

    def test_put_update_existing_bug_tracker_bugs(self):
        """PUT to update an existing bug_tracker_bug instance."""
        r_dict0, status_code = self.make_bug_tracker_bug()
        original_bug_id = r_dict0['bug_id']
        before = models.BugTrackerBug.objects.filter(
            bug_id=original_bug_id).exists()
        self.assertTrue(before)
        time_before = models.BugTrackerBug.objects.get(
            bug_id=original_bug_id).updated_at
        updated_bug_id = utils.generate_random_string()
        data = {'bug_id': updated_bug_id}
        response = self.api_client.put('/api/{}/bug_tracker_bug/{}/'
                                       .format(self.version,
                                               r_dict0['uuid']), data=data)
        r_dict1 = self.deserialize(response)
        self.assertFalse(models.BugTrackerBug.objects.filter(
            bug_id=original_bug_id).exists(),
            msg="bug_id not updated")
        instance = models.BugTrackerBug.objects.filter(bug_id=updated_bug_id)
        after = instance.exists()
        self.assertTrue(after, msg="bug_id incorrectly updated")
        time_after = instance[0].updated_at
        self.assertNotIn('pk', r_dict1, msg="Primary key in response!")
        self.assertNotEqual(
            time_before, time_after,
            msg="Updated_at should have been updated!")

    def test_put_cannot_update_existing_bug_tracker_bugs_uuid(self):
        """PUT to update an existing bug instance."""
        r_dict, status_code = self.make_bug_tracker_bug()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        data = {'uuid': uuid2}
        before = models.BugTrackerBug.objects.filter(uuid=uuid2).exists()
        self.assertFalse(before)
        response = self.api_client.put('/api/{}/bug_tracker_bug/{}/'.format(
            self.version, uuid), data=data)

        after = models.BugTrackerBug.objects.filter(uuid=uuid2).exists()
        self.assertFalse(after, msg="Bug UUID has been altered!")

        new_r_dict = self.deserialize(response)

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(uuid2, new_r_dict['uuid'],
                            msg="UUID should not have been updated!")
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_put_can_update_existing_bug_tracker_bugs_bug_id(self):
        """PUT to update an existing bug_tracker_bug instance."""
        r_dict, status_code = self.make_bug_tracker_bug()
        uuid = r_dict['uuid']
        bug_id = r_dict['bug_id']
        bug_id2 = utils.generate_random_number_as_string(not_this=bug_id)
        data = {'bug_id': bug_id2}
        before = models.BugTrackerBug.objects.filter(bug_id=bug_id2).exists()
        self.assertFalse(before)

        response = self.api_client.put('/api/{}/bug_tracker_bug/{}/'.format(
            self.version, uuid), data=data)

        after = models.BugTrackerBug.objects.filter(bug_id=bug_id2).exists()
        self.assertTrue(after, msg="Bug id has not been altered!")
        new_r_dict = self.deserialize(response)

        self.assertNotEqual(bug_id, new_r_dict['bug_id'],
                            msg="Bug id should have been updated!")
        self.assertEqual(bug_id2, new_r_dict['bug_id'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_get_all_bug_tracker_bugs(self):
        """GET all bug_tracker_bug instances."""
        bug_tracker_bug_dict = []
        for _ in range(3):
            bug_tracker_bug_dict.append(self.make_bug_tracker_bug())
        response = self.api_client.get('/api/{}/bug_tracker_bug/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        bug_ids = [obj['bug_id'] for obj in objects]
        for idx, ptrn in enumerate(bug_tracker_bug_dict):
            self.assertIn(ptrn[0]['bug_id'], bug_ids)

    def test_get_specific_bug_tracker_bug(self):
        """GET a specific bug_tracker_bug instance by its UUID."""
        r_dict0, status_code = self.make_bug_tracker_bug()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/bug_tracker_bug/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)
        self.assertEqual(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_delete_bug_tracker_bug(self):
        """DELETE an existing bug_tracker_bug instance."""
        r_dict0, status_code = self.make_bug_tracker_bug()
        uuid = r_dict0['uuid']
        self.assertTrue(models.BugTrackerBug.objects.filter(uuid=uuid)
                        .count() > 0)
        response = self.api_client.delete('/api/{}/bug_tracker_bug/{}/'
                                          .format(self.version, uuid),
                                          format='json')

        non_obj = models.BugTrackerBug.objects.filter(uuid=uuid)
        self.assertEqual(non_obj.count(), 0, msg="Bug not deleted")
        self.assertEqual(response.status_code, 204,
                         msg="Incorrect status code")


class BugOccurrenceResourceTests(ResourceTests):

    def test_post_create_bug_occurrence(self):
        regex = self.make_known_bug_regex()[0].get('uuid')
        build = self.make_build()[0].get('uuid')
        r_dict, statuscode = self.make_bug_occurrence(
            regex=regex, build=build)
        self.assertEqual(statuscode, 201, msg="Incorrect status code")
        self.assertIn(build, r_dict['build'])
        self.assertIn(regex, r_dict['regex'])

    def test_post_cannot_create_two_bug_occurrences_with_same_buildregex(self):
        regex = self.make_known_bug_regex()[0].get('uuid')
        build = self.make_build()[0].get('uuid')
        r_dict, statuscode = self.make_bug_occurrence(
            regex=regex, build=build)
        self.assertEqual(statuscode, 201, msg="Incorrect status code")
        self.assertIn(build, r_dict['build'])
        self.assertIn(regex, r_dict['regex'])

        with self.assertRaises(IntegrityError):
            self.make_bug_occurrence(regex=regex, build=build)

    def test_put_update_existing_bug_occurrences(self):
        """PUT to update an existing bug_occurrence instance."""
        original_regex = self.make_known_bug_regex()[0].get('uuid')
        r_dict0, statuscode0 = self.make_bug_occurrence(regex=original_regex)
        self.assertEqual(statuscode0, 201, msg="Incorrect status code")
        updated_regex = self.make_known_bug_regex()[0].get('uuid')
        before = original_regex in [regex.uuid for regex in
                                    models.BugOccurrence.objects.all()]
        self.assertFalse(before)
        data = {'regex': updated_regex}
        response = self.api_client.put(
            '/api/{}/bug_occurrence/{}/'.format(self.version, r_dict0['uuid']),
            data=data)
        r_dict1 = self.deserialize(response)
        after = original_regex in [regex.uuid for regex in
                                   models.BugOccurrence.objects.all()]
        self.assertFalse(after, msg="The regex was not updated")
        self.assertNotIn('pk', r_dict1, msg="Primary key in response!")

    def test_put_cannot_update_existing_bug_occurrences_uuid(self):
        """PUT to update an existing bug instance."""
        r_dict, status_code = self.make_bug_occurrence()
        uuid = r_dict['uuid']
        uuid2 = utils.generate_uuid()
        data = {'uuid': uuid2}
        before = models.BugOccurrence.objects.filter(uuid=uuid2).exists()
        self.assertFalse(before)
        response = self.api_client.put('/api/{}/bug_occurrence/{}/'.format(
            self.version, uuid), data=data)

        after = models.BugOccurrence.objects.filter(uuid=uuid2).exists()
        self.assertFalse(after, msg="Bug UUID has been altered!")

        new_r_dict = self.deserialize(response)

        self.assertEqual(uuid, new_r_dict['uuid'],
                         msg="UUID should not have been updated!")
        self.assertNotEqual(uuid2, new_r_dict['uuid'],
                            msg="UUID should not have been updated!")
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_get_all_bug_occurrences(self):
        """GET all bug_occurrence instances."""
        bug_occurrence_dict = []
        for _ in range(3):
            bug_occurrence_dict.append(self.make_bug_occurrence())
        response = self.api_client.get('/api/{}/bug_occurrence/'
                                       .format(self.version), format='json')
        r_dict = self.deserialize(response)
        objects = r_dict['objects']
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
        uuids = [obj['uuid'] for obj in objects]
        for idx, ptrn in enumerate(bug_occurrence_dict):
            self.assertIn(ptrn[0]['uuid'], uuids)

    def test_get_specific_bug_occurrence(self):
        """GET a specific bug_occurrence instance by its UUID."""
        r_dict0, status_code = self.make_bug_occurrence()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/bug_occurrence/{}/'
                                       .format(self.version, uuid),
                                       format='json')
        r_dict1 = self.deserialize(response)
        self.assertEqual(uuid, r_dict1['uuid'])
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")

    def test_delete_bug_occurrence(self):
        """DELETE an existing bug_occurrence instance."""
        r_dict0, status_code = self.make_bug_occurrence()
        uuid = r_dict0['uuid']
        self.assertTrue(models.BugOccurrence.objects.filter(uuid=uuid)
                        .count() > 0)
        response = self.api_client.delete('/api/{}/bug_occurrence/{}/'
                                          .format(self.version, uuid),
                                          format='json')

        non_obj = models.BugOccurrence.objects.filter(uuid=uuid)
        self.assertEqual(non_obj.count(), 0, msg="Bug not deleted")
        self.assertEqual(response.status_code, 204,
                         msg="Incorrect status code")

    def test_get_filter_by_uuid(self):
        r_dict0, status_code = self.make_bug_occurrence()
        uuid = r_dict0['uuid']
        response = self.api_client.get('/api/{}/bug_occurrence/?uuid={}'
                                       .format(self.version, uuid))
        r_dict = self.deserialize(response)['objects'][0]
        returned_uuid = r_dict['uuid']
        self.assertEqual(uuid, returned_uuid)

    def test_get_filter_by_regex(self):
        regex = self.make_known_bug_regex()[0].get('uuid')
        r_dict0, status_code = self.make_bug_occurrence(regex=regex)
        response = self.api_client.get('/api/{}/bug_occurrence/?regex__uuid={}'
                                       .format(self.version, regex))
        r_dict = self.deserialize(response)['objects'][0]
        returned_regex = r_dict['regex']
        self.assertIn(regex, returned_regex)

    def test_get_filter_by_build(self):
        build = self.make_build()[0].get('uuid')
        r_dict0, status_code = self.make_bug_occurrence(build=build)
        response = self.api_client.get('/api/{}/bug_occurrence/?build__uuid={}'
                                       .format(self.version, build))
        r_dict = self.deserialize(response)['objects'][0]
        returned_build = r_dict['build']
        self.assertIn(build, returned_build)

    def test_get_filter_by_regex_and_build(self):
        regex = self.make_known_bug_regex()[0].get('uuid')
        build = self.make_build()[0].get('uuid')
        r_dict0, status_code = self.make_bug_occurrence(
            regex=regex, build=build)
        response = self.api_client.get(
            '/api/{}/bug_occurrence/?regex__uuid={}&build__uuid={}'
            .format(self.version, regex, build))
        r_dict = self.deserialize(response)['objects'][0]
        returned_regex = r_dict['regex']
        returned_build = r_dict['build']
        self.assertIn(regex, returned_regex)
        self.assertIn(build, returned_build)
