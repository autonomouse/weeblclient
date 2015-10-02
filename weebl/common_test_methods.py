import random
import utils
from weebl import urls
from django.test import TestCase
from tastypie.test import ResourceTestCase
from oilserver import models


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


def make_environment():
    environment = models.Environment(
        name=utils.generate_random_string())
    environment.save()
    return environment


def make_jenkins(environment=None):
    if environment is None:
        if models.Environment.objects.exists():
            environment = models.Environment.objects.first()
        else:
            environment = make_environment()

    service_status = models.ServiceStatus.objects.get(name='up')

    jenkins = models.Jenkins(
        environment=environment,
        service_status=service_status,
        external_access_url=utils.generate_random_string())
    jenkins.save()
    return jenkins


def make_build_executor(jenkins=None):
    if jenkins is None:
        if models.Jenkins.objects.exists():
            jenkins = models.Jenkins.objects.first()
        else:
            jenkins = make_jenkins()
    build_executor = models.BuildExecutor(jenkins=jenkins)
    build_executor.save()
    return build_executor


def make_pipeline(build_executor=None):
    if build_executor is None:
        build_executor = make_build_executor()

    pipeline = models.Pipeline(build_executor=build_executor)
    pipeline.save()
    return pipeline


def make_ubuntu_version(self, name=None, number=None):
    if name is None:
        name = utils.generate_random_string()
    if number is None:
        number = utils.generate_random_string()
    data = {'name': name,
            'number': number}
    return self.post_create_instance_without_status_code(
        'ubuntuversion', data=data)


def make_openstack_version(self, name=None):
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


def make_compute(self, name=None):
    if name is None:
        name = utils.generate_random_string()
    data = {'name': name}
    return self.post_create_instance_without_status_code(
        'compute', data=data)


def make_block_storage(self, name=None):
    if name is None:
        name = utils.generate_random_string()
    data = {'name': name}
    return self.post_create_instance_without_status_code(
        'block_storage', data=data)


def make_image_storage(self, name=None):
    if name is None:
        name = utils.generate_random_string()
    data = {'name': name}
    return self.post_create_instance_without_status_code(
        'image_storage', data=data)


def make_database(self, name=None):
    if name is None:
        name = utils.generate_random_string()
    data = {'name': name}
    return self.post_create_instance_without_status_code(
        'database', data=data)


def make_build(build_id=None, build_status=None, job_type=None, pipeline=None):
    if build_id is None:
        build_id = str(random.randint(1, 1000000))

    if build_status is None:
        build_status = models.BuildStatus.objects.get(name='success')

    if job_type is None:
        job_type = models.JobType.objects.get(name='pipeline_deploy')

    if pipeline is None:
        pipeline = make_pipeline()

    build = models.Build(
        build_id=build_id,
        build_status=build_status,
        job_type=job_type,
        pipeline=pipeline)
    build.save()
    return build


def make_bug():
    bug = models.Bug(summary=utils.generate_random_string())
    bug.save()
    return bug


def make_known_bug_regex(bug=None):
    if bug is None:
        bug = make_bug()

    regex = models.KnownBugRegex(
        regex=utils.generate_random_string(),
        bug=bug)
    regex.save()
    return regex


def make_bug_occurrence(regex=None, build=None):
    if regex is None:
        regex = make_known_bug_regex()

    if build is None:
        build = make_build()

    bug_occurrence = models.BugOccurrence(regex=regex, build=build)
    bug_occurrence.save()
    return bug_occurrence
