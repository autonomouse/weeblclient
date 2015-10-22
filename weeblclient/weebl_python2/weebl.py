import json
import requests
import six
if six.PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin
from datetime import datetime
from weeblclient.weebl_python2 import utils
from requests.exceptions import ConnectionError
from weeblclient.weebl_python2.exception import UnexpectedStatusCode


class Weebl(object):
    """Weebl API wrapper class."""

    def __init__(self, uuid, env_name,
                 weebl_url="http://10.245.0.14",
                 weebl_api_ver="v1",
                 weebl_auth=('weebl', 'passweebl')):
        self.LOG = utils.get_logger("weeblSDK_python2")
        self.env_name = env_name
        self.uuid = uuid
        self.weebl_api_version = weebl_api_ver
        self.weebl_url = weebl_url
        self.weebl_auth = weebl_auth
        self.headers = {"content-type": "application/json",
                        "limit": None}
        self.resource_url = "/api/{}/".format(weebl_api_ver)
        self.base_url = urljoin(weebl_url, self.resource_url)
        self._jenkins_uuid = None

    def make_url(self, *path_list, **kwargs):
        query = kwargs.get('query')
        path = "/".join([item.lstrip('/').rstrip('/') for item in path_list])
        url = urljoin(self.base_url, path) + '/'
        if query is not None:
            return url + query
        return url

    def make_request(self, method, raise_exception=True, **payload):
        payload['headers'] = self.headers
        # payload['auth'] = self.weebl_auth
        try:
            if method == 'get':
                response = requests.get(**payload)
            elif method == 'post':
                response = requests.post(**payload)
            elif method == 'put':
                response = requests.put(**payload)
            elif method == 'delete':
                response = requests.delete(**payload)
        except ConnectionError as e:
            msg = "Could not connect to Weebl server {}:\n\n {}\n".format(
                payload['url'], e)
            self.LOG.error(msg)
            if raise_exception:
                raise(e)

        # If response code isn't 2xx:
        if str(response.status_code)[0] != '2':
            msg = "Request returned a status code of {}:\n\n {}\n".format(
                response.status_code, response.text)
            self.LOG.error(msg)
            if raise_exception:
                raise UnexpectedStatusCode(msg)
        return response

    def get_objects(self, obj, params=None):
        return self.get_instances(obj, params=params).get('objects')

    def get_instances(self, obj, params=None):
        """Returns a single instance from the url that is made up of the
        base_url and the given 'obj' path, where obj is the part of the url
        that follows the base_url (e.g. base_url is http://www.foo.bar/ and the
        obj is foobar in this url: http://www.foo.bar/foobar/).
        """
        response = self.make_request(
            'get', url=self.make_url(obj), params=params)
        try:
            return response.json()
        except ValueError:
            return []
        except UnexpectedStatusCode:
            return []

    def get_instance_data(self, obj, field, obj_field_path, instance_id):
        data = {obj_field_path: instance_id}
        return self.get_objects(obj, params=data)

    def instance_exists(self, obj, field, obj_field_path, instance_id):
        matching_instances = self.get_instance_data(
            obj, field, obj_field_path, instance_id)
        if instance_id in [instance.get(field) for instance in
                           matching_instances]:
            return True
        return False

    def filter_instances(self, obj, filters):
        filter_by = '?'
        for num, fltr in enumerate(filters):
            filter_by += "{}={}".format(fltr[0], fltr[1])
            if num != (len(filters) - 1):
                filter_by += "&"
        url = self.make_url(obj, query=filter_by)
        return self.get_objects(url)

    def weeblify_environment(self, jenkins_host, ci_server_api=None):
        self.set_up_new_environment()
        self.set_up_new_jenkins(jenkins_host)
        if ci_server_api is not None and hasattr(ci_server_api, 'jenkins_api'):
            self.set_up_new_buildexecutors(ci_server_api.jenkins_api)

    def weeblify_environment_jenkinsAPI(self, jenkins_host, jenkins_api):
        self.set_up_new_environment()
        self.set_up_new_jenkins(jenkins_host)
        self.set_up_new_buildexecutors(jenkins_api)

    def environment_exists(self, env_uuid):
        return self.instance_exists(
            'environment', 'uuid', 'environment_uuid', env_uuid)

    def jenkins_exists(self, jenkins_uuid):
        return self.instance_exists(
            'jenkins', 'uuid', 'jenkins_uuid', jenkins_uuid)

    def buildexecutor_exists(self, name):
        buildexecutor_instances = self.filter_instances(
            "buildexecutor", [
                ('name', name),
                ('jenkins__uuid', self._get_jenkins_uuid()),
            ]
        )
        return len(buildexecutor_instances) > 0

    def pipeline_exists(self, pipeline_id):
        return self.instance_exists(
            'pipeline', 'uuid', 'pipeline_uuid', pipeline_id)

    def build_exists(self, build_uuid):
        return self.instance_exists(
            'build', 'uuid', 'build_uuid', build_uuid)

    def knownbugregex_exists(self, regex):
        knownbugregex_instances = self.get_instance_data(
            'knownbugregex', 'regex', 'knownbugregex_regex', regex)
        if knownbugregex_instances != []:
            if regex in [kbr.get('regex') for kbr in
                         knownbugregex_instances]:
                return knownbugregex_instances[0]['resource_uri']
        return False

    def bugoccurrence_exists(self, build_uuid, regex_uuid):
        bugoccurrence_instances = self.filter_instances(
            "bugoccurrence", [('build__uuid', build_uuid),
                              ('regex__uuid', regex_uuid)])
        return len(bugoccurrence_instances) > 0

    def targetfileglob_exists(self, glob_pattern):
        return self.instance_exists(
            'targetfileglob', 'glob_pattern', 'targetfileglob_glob_pattern',
            glob_pattern)

    def bugtrackerbug_exists(self, bug_number):
        bugtrackerbug_instances = self.get_instance_data(
            'bugtrackerbug', 'bug_number', 'bugtrackerbug_bug_number',
            bug_number)
        if bugtrackerbug_instances is not None:
            if bug_number in [str(btbugs.get('bug_number')) for btbugs in
                              bugtrackerbug_instances]:
                return bugtrackerbug_instances[0]['resource_uri']
        return False

    def bug_exists(self, summary):
        return self.instance_exists('bug', 'summary', 'bug_summary', summary)

    def _get_jenkins_uuid(self):
        if self._jenkins_uuid is None:
            jenkins = self.get_instance_data(
                'jenkins', 'uuid', 'environment__uuid', self.uuid)
            if len(jenkins) > 0:
                self._jenkins_uuid = jenkins[0]['uuid']
            else:
                self._jenkins_uuid = None
        return self._jenkins_uuid

    def get_build_uuid_from_build_id_and_pipeline(self, build_id,
                                                  pipeline_uuid):
        build_instances = self.filter_instances(
            "build", [('build_id', build_id),
                      ('pipeline_uuid', pipeline_uuid)])
        if build_instances is not None:
            if build_id in [str(build.get('build_id')) for build in
                            build_instances]:
                return build_instances[0]['resource_uri']
        return False

    def set_up_new_buildexecutors(self, ci_server_api):
        newly_created_buildexecutors = []

        for buildexecutor in ci_server_api.get_nodes().iteritems():
            name = buildexecutor[0]
            if self.buildexecutor_exists(name):
                continue
            # Create this build executor for this environment:
            self.create_buildexecutor(name)
            newly_created_buildexecutors.append(name)
        if newly_created_buildexecutors != []:
            msg = "Created the following {} environment build executor(s):\n{}"
            self.LOG.info(msg.format(self.env_name,
                          newly_created_buildexecutors))

    def set_up_new_environment(self):
        if self.environment_exists(self.uuid):
            self.LOG.info("Environment exists with UUID: {}".format(self.uuid))
            env_name = self.get_env_name_from_uuid(self.uuid)
            if env_name != self.env_name:
                msg = "Environment name provided ({0}) does not match the "
                msg += "name of the environment with uuid: {1}, which is {2}. "
                msg += "Using {2} as environment name instead."
                self.LOG.error(
                    msg.format(self.env_name, self.uuid, env_name))
                self.env_name = env_name
            return

        # Create new environment:
        url = self.make_url("environment")
        data = {'name': self.env_name,
                'uuid': self.uuid}
        response = self.make_request('post', url=url, data=json.dumps(data))
        self.env_name = response.json()['name']
        self.LOG.info("Set up new {} environment: {}".format(
            self.env_name, self.uuid))

    def _pk_uri(self, resource, value):
        return "/api/%s/%s/%s/" % (
            self.weebl_api_version, resource, value)

    def set_up_new_jenkins(self, jenkins_host):
        jenkins_uuid = self._get_jenkins_uuid()
        if self.jenkins_exists(jenkins_uuid):
            self.LOG.info(
                "Jenkins exists for environment with UUID: {}".format(
                    self.uuid))
            return

        # Create new jenkins:
        url = self.make_url("jenkins")
        data = {
            'environment': self._pk_uri('environment', self.uuid),
            'external_access_url': jenkins_host,
            'internal_access_url': jenkins_host,
            'servicestatus': self._pk_uri('servicestatus', 'up'),
        }
        self.make_request('post', url=url, data=json.dumps(data))
        self.LOG.info("Set up new jenkins '{}' for environment {}".format(
            self._get_jenkins_uuid(), self.uuid))

    def check_in_to_jenkins(self, ci_server_api):
        url = self.make_url("jenkins", self._get_jenkins_uuid())
        response = self.make_request('put', url=url, data=json.dumps({}))
        return response.json().get('uuid')

    def create_buildexecutor(self, buildexecutor_name):
        jenkins_resource_uri = self._pk_uri(
            'jenkins', self._get_jenkins_uuid())
        url = self.make_url("buildexecutor")
        data = {'name': buildexecutor_name,
                'jenkins': jenkins_resource_uri}
        self.make_request('post', url=url, data=json.dumps(data))

    def create_pipeline(self,
                        pipeline_id,
                        buildexecutor_name,
                        ubuntuversion=None,
                        openstackversion=None,
                        sdn=None,
                        compute=None,
                        blockstorage=None,
                        imagestorage=None,
                        database=None):
        # Get Build Executor:
        buildexecutor = self.get_buildexecutor_uuid_from_name(
            buildexecutor_name)

        # Create pipeline:
        url = self.make_url("pipeline")
        data = {
            'buildexecutor': self._pk_uri('buildexecutor', buildexecutor),
            'uuid': pipeline_id, }

        if ubuntuversion is not None:
            data['ubuntuversion'] = ubuntuversion,

        if openstackversion is not None:
            data['openstackversion'] = openstackversion,

        if sdn is not None:
            data['sdn'] = sdn,

        if compute is not None:
            data['compute'] = compute,

        if blockstorage is not None:
            data['blockstorage'] = blockstorage,

        if imagestorage is not None:
            data['imagestorage'] = imagestorage,

        if database is not None:
            data['database'] = database

        response = self.make_request('post', url=url, data=json.dumps(data))
        self.LOG.info("Pipeline {} successfully created in Weebl db"
                      .format(pipeline_id))
        returned_pipeline = response.json().get('uuid')

        # Error if pipelines do not match:
        if returned_pipeline != pipeline_id:
            msg = ("Pipeline created on weebl does not match: {} != {}"
                   .format(pipeline_id, returned_pipeline))
            self.LOG.error(msg)
            raise Exception(msg)

        return returned_pipeline

    def update_completed_pipeline(self, pipeline_id, completed_at=None):
        if completed_at is None:
            completed_at = datetime.now()
        url = self.make_url("pipeline", pipeline_id)
        data = {'pipeline': pipeline_id,
                'completed_at': completed_at}
        response = self.make_request('put', url=url, data=json.dumps(data))
        return response.json().get('completed_at')

    def create_knownbugregex(self, glob_patterns_list, regex):

        # Create knownbugregex:
        url = self.make_url("knownbugregex")
        data = {"targetfileglobs": glob_patterns_list,
                "regex": regex}
        response = self.make_request('post', url=url, data=json.dumps(data))
        return response.json()['resource_uri']

    def create_targetfileglob(self, glob_pattern, jobtypes_list=None):
        # Create targetfileglob:
        data = {"glob_pattern": glob_pattern, }

        if jobtypes_list is not None:
            data["jobtypes"] = jobtypes_list

        url = self.make_url("targetfileglob")
        self.make_request('post', url=url, data=json.dumps(data))

    def create_bug(self, summary, bugtrackerbug=None, knownbugregex_list=None):
        # Create bug:
        url = self.make_url("bug")
        data = {}
        data["summary"] = summary
        data["description"] = data["summary"]

        if bugtrackerbug is not None:
            data['bugtrackerbug'] = bugtrackerbug

        if knownbugregex_list is not None:
            data['knownbugregex'] = knownbugregex_list
        self.make_request('post', url=url, data=json.dumps(data))

    def create_bugtrackerbug(self, bug_number):
        # Create bugtrackerbug:
        url = self.make_url("bugtrackerbug")
        data = {"bug_number": bug_number}
        response = self.make_request('post', url=url, data=json.dumps(data))
        return response.json()['resource_uri']

    def get_env_name_from_uuid(self, uuid):
        url = self.make_url("environment", uuid)
        response = self.make_request('get', url=url)
        return response.json().get('name')

    def get_env_uuid_from_name(self, name):
        url = self.make_url("environment", "by_name", name)
        response = self.make_request('get', url=url)
        return response.json().get('uuid')

    def get_buildexecutor_uuid_from_name(self, buildexecutor_name):
        url = self.make_url("buildexecutor")
        url_with_args = "{}?jenkins__uuid={}&name={}".format(
            url, self._get_jenkins_uuid(), buildexecutor_name)
        response = self.make_request('get', url=url_with_args)
        objects = response.json()['objects']

        if objects == []:
            return
        else:
            return objects[0].get('uuid')

    def create_build(self, build_id, pipeline, jobtype, buildstatus,
                     build_started_at=None, build_finished_at=None,
                     ts_format="%Y-%m-%d %H:%M:%SZ"):
        # Create build:
        url = self.make_url("build")
        data = {
            'build_id': build_id,
            'pipeline': self._pk_uri('pipeline', pipeline),
            'buildstatus': self._pk_uri('buildstatus', buildstatus),
            'jobtype': self._pk_uri('jobtype', jobtype)}
        if build_started_at:
            data['build_started_at'] =\
                utils.convert_timestamp_to_string(build_started_at, ts_format)
        if build_finished_at:
            data['build_finished_at'] =\
                utils.convert_timestamp_to_string(build_finished_at, ts_format)

        response = self.make_request('post', url=url, data=json.dumps(data))
        response_data = response.json()
        build_uuid = response_data['uuid']
        self.LOG.info("Build {} successfully created (build uuid: {})"
                      .format(build_id, build_uuid))
        return build_uuid

    def update_build(self, build_id, pipeline, jobtype, buildstatus,
                     build_started_at=None, build_finished_at=None,
                     ts_format="%Y-%m-%d %H:%M:%SZ"):
        # Update build:
        url = self.make_url("build", build_id)
        data = {
            'pipeline': self._pk_uri('pipeline', pipeline),
            'buildstatus': self._pk_uri('buildstatus', buildstatus),
            'jobtype': self._pk_uri('jobtype', jobtype)}
        if build_started_at:
            data['build_started_at'] =\
                utils.convert_timestamp_to_string(build_started_at, ts_format)
        if build_finished_at:
            data['build_finished_at'] =\
                utils.convert_timestamp_to_string(build_finished_at, ts_format)

        response = self.make_request('put', url=url, data=json.dumps(data))
        response_data = response.json()
        build_uuid = response_data['uuid']
        self.LOG.info("Build {} successfully created (build uuid: {})"
                      .format(build_id, build_uuid))
        return build_uuid

    def create_bugoccurrence(self, build_uuid, regex_uuid):
        # Create Bug Occurrence:
        url = self.make_url("bugoccurrence")
        data = {
            'build': self._pk_uri('build', build_uuid),
            'regex': self._pk_uri('knownbugregex', regex_uuid)
        }
        response = self.make_request('post', url=url, data=json.dumps(data))
        bugoccurrence_uuid = response.json().get('uuid')
        self.LOG.info("Bug Occurrence created (bug occurrence uuid: {})"
                      .format(bugoccurrence_uuid))
        return bugoccurrence_uuid

    def get_bug_info(self, force_refresh=True):
        self.LOG.info("Downloading bug regexs from Weebl: {}"
                      .format(self.weebl_url))
        target_file_globs = self.get_objects("targetfileglob")
        known_bug_regexes = self.get_objects("knownbugregex")
        bugs = self.get_objects("bug")
        return utils.munge_bug_info_data(
            target_file_globs, known_bug_regexes, bugs)
