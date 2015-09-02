import utils
import random
from weebl import urls
from oilserver import models
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
        if env_uuid is None:
            env_uuid, env_name = self.make_environment_and_jenkins()
        if name is None:
            data = {'jenkins': env_uuid}
        else:
            data = {'name': name,
                    'jenkins': env_uuid}
        return self.post_create_instance('build_executor', data=data)

    def make_pipeline(self, build_executor=None, pipeline=None):
        if build_executor is None:
            response = self.make_build_executor()
            build_executor = response[0]['uuid']
        data = {'build_executor': build_executor}
        if pipeline is not None:
            data['pipeline'] = pipeline
        return self.post_create_instance('pipeline', data=data)

    def make_build(self, pipeline=None):
        if pipeline is None:
            response = self.make_pipeline()
            pipeline = response[0]['uuid']
        build_id = str(random.randint(10000, 99999))
        build_status = models.BuildStatus.objects.all()[1].name
        job_type = models.JobType.objects.all()[0].name
        data = {'build_id': str(build_id),
                'pipeline': pipeline,
                'build_status': build_status,
                'job_type': job_type}
        return self.post_create_instance('build', data=data)

    def make_target_file_glob(self):
        name = utils.generate_random_string()
        data = {'glob_pattern': name}
        return self.post_create_instance('target_file_glob', data=data)

    def make_known_bug_regex(self, target_file_globs=None):
        if target_file_globs is None:
            x = random.randint(2, 9)
            target_file_globs = [utils.generate_random_string() for _ in
                                 range(x)]
        data = {"target_file_globs": target_file_globs,
                "regex": utils.generate_random_string()}
        return self.post_create_instance('known_bug_regex', data=data)
