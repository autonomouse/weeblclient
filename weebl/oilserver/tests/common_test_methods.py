import random
import utils
from weebl import urls
from django.test import TestCase
from tastypie.test import ResourceTestCase
from oilserver import models
from django.contrib.auth.models import User


class WeeblTestCase(TestCase):
    fixtures = ['initial_settings.yaml']


class ResourceTests(ResourceTestCase):
    version = urls.v_api.api_name
    fixtures = ['initial_settings.yaml']

    def setUp(self):
        super(ResourceTests, self).setUp()

        # Create mock user:
        self.username = 'mock_user'
        email = "{}@example.com".format(self.username)
        user = User.objects.create_user(self.username, email)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save()
        self.api_key = User.objects.get(username=self.username).api_key.key

    def get_credentials(self):
        return self.create_apikey(
            username=self.username, api_key=self.api_key)

    def post_create_instance(self, model, data):
        response = self.api_client.post(
            '/api/{}/{}/'.format(self.version, model), data=data,
            authentication=self.get_credentials())
        return (self.deserialize(response), response.status_code)

    def post_create_instance_without_status_code(self, model, data):
        return self.post_create_instance(model, data)[0]

    def make_environment_via_api(self, name=None):
        if name is None:
            name = utils.generate_random_string()
        data = {'name': name}
        return self.post_create_instance_without_status_code(
            'environment', data=data)


def make_environment(name=None):
    if name is None:
        name = utils.generate_random_string()
    environment = models.Environment(name=name)
    environment.save()
    return environment


def make_jenkins(environment=None):
    if environment is None:
        if models.Environment.objects.exists():
            environment = models.Environment.objects.first()
        else:
            environment = make_environment()

    servicestatus = models.ServiceStatus.objects.get(name='up')

    jenkins = models.Jenkins(
        environment=environment,
        servicestatus=servicestatus,
        external_access_url=utils.generate_random_string())
    jenkins.save()
    return jenkins


def make_buildexecutor(jenkins=None):
    if jenkins is None:
        if models.Jenkins.objects.exists():
            jenkins = models.Jenkins.objects.first()
        else:
            jenkins = make_jenkins()
    buildexecutor = models.BuildExecutor(jenkins=jenkins)
    buildexecutor.save()
    return buildexecutor


def make_pipeline(buildexecutor=None):
    if buildexecutor is None:
        if models.BuildExecutor.objects.exists():
            buildexecutor = models.BuildExecutor.objects.first()
        else:
            buildexecutor = make_buildexecutor()
    pipeline = models.Pipeline(buildexecutor=buildexecutor)
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
    return self.post_create_instance_without_status_code('sdn', data=data)


def make_compute(self, name=None):
    if name is None:
        name = utils.generate_random_string()
    data = {'name': name}
    return self.post_create_instance_without_status_code('compute', data=data)


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


def make_build(build_id=None, buildstatus=None, jobtype=None, pipeline=None):
    if build_id is None:
        build_id = str(random.randint(1, 1000000))

    if buildstatus is None:
        buildstatus = models.BuildStatus.objects.get(name='success')

    if jobtype is None:
        jobtype = models.JobType.objects.get(name='pipeline_deploy')

    if pipeline is None:
        pipeline = make_pipeline()

    build = models.Build(
        build_id=build_id,
        buildstatus=buildstatus,
        jobtype=jobtype,
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


def make_bugoccurrence(regex=None, build=None):
    if regex is None:
        regex = make_known_bug_regex()

    if build is None:
        build = make_build()

    bugoccurrence = models.BugOccurrence(regex=regex, build=build)
    bugoccurrence.save()
    return bugoccurrence
