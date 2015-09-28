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

    def make_pipeline(self, build_executor=None, pipeline=None, sdn=None,
                      ubuntu_version='trusty', openstack_version='havana'):
        if build_executor is None:
            response = self.make_build_executor()
            build_executor = response[0]['uuid']
        data = {'build_executor': build_executor}
        if pipeline is not None:
            data['pipeline'] = pipeline
        data['ubuntu_version'] = ubuntu_version
        data['openstack_version'] = openstack_version
        if sdn is None:
            data['sdn'] = utils.generate_random_string()
        return self.post_create_instance('pipeline', data=data)

    def make_ubuntuversion(self, name=None, number=None):
        if name is None:
            name = utils.generate_random_string()
        if number is None:
            number = utils.generate_random_string()
        data = {'name': name,
                'number': number}
        a = self.post_create_instance_without_status_code(
            'ubuntuversion', data=data)


        print(a)


        return a

    def make_openstackversion(self, name=None):
        if name is None:
            name = utils.generate_random_string()
        data = {'name': name}
        return self.post_create_instance_without_status_code(
            'openstackversion', data=data)

    def make_sdn(self, name=None):
        if name is None:
            name = utils.generate_random_string()
        data = {'name': name}
        return self.post_create_instance_without_status_code(
            'sdn', data=data)

    def make_build(self, pipeline=None):
        if pipeline is None:
            response = self.make_pipeline()
            pipeline = response[0]['uuid']
        build_id = utils.generate_random_number_as_string()
        build_status = models.BuildStatus.objects.all()[1].name
        job_type = models.JobType.objects.all()[0].name
        data = {'build_id': str(build_id),
                'pipeline': pipeline,
                'build_status': build_status,
                'job_type': job_type}
        return self.post_create_instance('build', data=data)

    def make_target_file_glob(self, job_types=None):
        name = utils.generate_random_string()
        data = {'glob_pattern': name}
        if job_types is not None:
            data['job_types'] = job_types
        return self.post_create_instance('target_file_glob', data=data)

    def make_known_bug_regex(self, target_file_globs=None, bug=None):
        if target_file_globs is None:
            x = random.randint(2, 9)
            target_file_globs = [utils.generate_random_string() for _ in
                                 range(x)]
        data = {"target_file_globs": target_file_globs,
                "regex": utils.generate_random_string()}
        if bug is not None:
            data['bug'] = bug
        return self.post_create_instance('known_bug_regex', data=data)

    def make_bug(self, uuid=None, summary=None, description=None):
        data = {'summary': summary if summary is not None else
                utils.generate_random_string()}
        if uuid is not None:
            data['uuid'] = uuid
        if description is not None:
            data['description'] = description
        return self.post_create_instance('bug', data=data)

    def make_bug_tracker_bug(self, bug_id=None):
        if bug_id is None:
            bug_id = utils.generate_random_number_as_string()
        data = {'bug_id': bug_id}
        return self.post_create_instance('bug_tracker_bug', data=data)

    def make_bug_occurrence(self, regex=None, build=None):
        if regex is None:
            regex = self.make_known_bug_regex()[0].get('uuid')
        if build is None:
            build = self.make_build()[0].get('uuid')
        data = {'regex': regex, 'build': build}
        return self.post_create_instance('bug_occurrence', data=data)
