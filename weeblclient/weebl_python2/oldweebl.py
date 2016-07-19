import re
import json
import requests
from fnmatch import fnmatch
from datetime import datetime
from requests.exceptions import ConnectionError
from six.moves.urllib_parse import urljoin
from six.moves import urllib
from weeblclient.weebl_python2 import utils
from weeblclient.weebl_python2.exception import (
    UnexpectedStatusCode,
    UnrecognisedInstance,
)
from weeblclient.weebl_python2.tastypie_client import Requester

class OldWeebl(object):
    def __init__(self, uuid, env_name, username=None, apikey=None,
                 weebl_url="http://10.245.0.14",
                 weebl_api_ver="v1"):
        self.username = username
        self.LOG = utils.get_logger("weeblSDK_python2")
        self.env_name = env_name
        self.uuid = uuid
        self.weebl_api_version = weebl_api_ver
        self.weebl_url = weebl_url
        self.resource_url = "/api/{}/".format(weebl_api_ver)
        self.base_url = urljoin(weebl_url, self.resource_url)
        self.requester = Requester(self.base_url, username, apikey)
        self._jenkins_uuid = None

    def make_url(self, *path_list, **kwargs):
        return self.requester.make_url(*path_list, **kwargs)

    def make_request(self, method, **payload):
        return self.requester.make_request(method, **payload)

    def get_objects(self, obj, params=None, query=None):
        return self.get_instances(
            obj, params=params, query=query).get('objects')

    def get_instances(self, obj, params=None, query=None):
        """Returns instance(s) from the url that is made up of the
        base_url and the given 'obj' path, where obj is the part of the url
        that follows the base_url (e.g. base_url is http://www.foo.bar/ and the
        obj is foobar in this url: http://www.foo.bar/foobar/).
        """
        response = self.make_request(
            'get', url=self.make_url(obj, query=query), params=params)
        return self.respond(response)

    def get_instances_from_url(self, url, params=None):
        """Returns instance(s) from the given url."""
        response = self.make_request('get', url=url, params=params)
        return self.respond(response)

    def respond(self, response):
        """Returns json from the response or catches the usual errors.
        """
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
        filter_by = '?' + "&".join(
            ["{}={}".format(k, v) for k, v in filters.items()]
        )
        return self.get_objects(obj, query=filter_by)

    def update_instance(self, url, **kwargs):
        response = self.make_request('put', url=url, data=json.dumps(kwargs))

        try:
            return response.json()
        except ValueError:
            return []
        except UnexpectedStatusCode:
            return []

    def pk_uri(self, resource, value):
        """ This method builds a resource uri for a given model. The Weebl API
        does not tend to use the primary key of a model resource for its uri,
        instead they usually use a model's uuid or name.
        """
        return "/api/%s/%s/%s/" % (
            self.weebl_api_version, resource, value)

    def get_pk_from_resource_uri(self, resource_uri):
        """ This method is basically the inverse of the pk_uri method. It gets
        the endpoint name from the resource uri. The endpoint name is the
        primary key by default, but weebl usually overrides this with the uuid
        of the model. In some cases when there isn't a uuid, "name" is often
        used instead.
        """
        return resource_uri.rstrip('/').split('/')[-1]

    # Set Up:
    def weeblify_environment(self, jenkins_host, ci_server_api=None):
        jenkins_api = None
        if ci_server_api is not None and hasattr(ci_server_api, 'jenkins_api'):
            jenkins_api = ci_server_api.jenkins_api
        self.weeblify_environment_jenkinsAPI(jenkins_host, jenkins_api)

    def weeblify_environment_jenkinsAPI(self, jenkins_host, jenkins_api=None):
        self.set_up_new_environment()
        self.set_up_new_jenkins(jenkins_host)
        if jenkins_api is not None:
            self.set_up_new_buildexecutors(jenkins_api)

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
            else:
                self.LOG.info("Environment name: '{}'".format(self.env_name))
            return
        self.create_environment(self.env_name, self.uuid)

    def set_up_new_jenkins(self, jenkins_host):
        jenkins_uuid = self._get_jenkins_uuid()
        if self.jenkins_exists(jenkins_uuid):
            self.LOG.info(
                "Jenkins exists for environment with UUID: {}".format(
                    self.uuid))
            return
        self.create_jenkins(self.uuid, jenkins_host)

    def apply_all_regexes_to_text(self, text, target_file):
        knownbugregex_instances = self.get_instances("knownbugregex")

        for knownbugregex in knownbugregex_instances:
            regex = knownbugregex['regex']
            regex_uuid = knownbugregex['uuid']
            targetfileglobs = [
                tf['glob_pattern'] for tf in
                knownbugregex['targetfileglobs']]
            matching_tfiles = [glob for glob in targetfileglobs if
                               fnmatch(target_file, glob)]
            if len(matching_tfiles) <= 0:
                return
            matches = re.compile(regex, re.DOTALL).findall(text)
            if len(matches) > 0:
                msg = "Unfiled bug matched to {}:\n{}"
                self.LOG.info(msg.format(regex_uuid, regex))
                return regex_uuid

    def set_up_test_framework_caseclass_and_case(self, testframework_name,
                                                 version, testcaseclass_name,
                                                 testcase_name):
        testframework_uuid = self.get_or_create_testframework(
            name=testframework_name, version=version)
        testcaseclass_uuid = self.get_or_create_testcaseclass(
            name=testcaseclass_name, testframework_uuid=testframework_uuid)
        return self.get_or_create_testcase(
            name=testcase_name, testcaseclass_uuid=testcaseclass_uuid)

    def set_up_build_framework_case_and_class(self, jobtype):
        # Version is only appropriate for test frameworks, use "notapplicable"
        # for builds:
        return self.set_up_test_framework_caseclass_and_case(
            testframework_name=jobtype, version="notapplicable",
            testcaseclass_name=jobtype, testcase_name=jobtype)

    # Bug
    def bug_exists(self, summary):
        return self.instance_exists('bug', 'summary', 'summary', summary)

    def create_bug(self, summary, bugtrackerbug=None):
        """Creates a new instance of the 'Bug' model.

        Args:
            summary: A string containing a summary of the bug.
            bugtrackerbug: A string containing the resource uri of the
                associated bug tracker bug.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """
        # Create bug:
        url = self.make_url("bug")
        data = {}
        data["summary"] = summary
        data["description"] = data["summary"]

        if bugtrackerbug is not None:
            data['bugtrackerbug'] = bugtrackerbug

        self.make_request('post', url=url, data=json.dumps(data))

    def get_bug_from_summary(self, summary):
        bug_instances = self.get_instance_data(
            'bug', 'summary', 'summary', summary)
        if bug_instances is not None:
            if summary in [str(bug.get('summary')) for bug in bug_instances]:
                return self.pk_uri('bug', bug_instances[0]['uuid'])

    def get_bug_regexes(self, bug_resource):
        return self.get_instances(bug_resource)['knownbugregexes']

    def update_bug_with_new_bug_regexes(self, regex_resource, bug_resource):
        url = self.make_url(regex_resource)
        self.update_instance(url, bug=bug_resource)

    # Bug Occurrence
    def bugoccurrence_exists(self, build_uuid, regex_uuid):
        bugoccurrence_instances = self.filter_instances(
            "bugoccurrence", {
                'testcaseinstance__build__uuid': build_uuid,
                'knownbugregex__uuid': regex_uuid
            }
        )
        return len(bugoccurrence_instances) > 0

    def create_bugoccurrence(self, testcaseinstance_uri, knownbugregex_uri):
        """Creates a new instance of the 'BugOccurrence' model.

        Args:
            testcaseinstance_uri: A string containing the testcaseinstance uri.
            knownbugregex_uri: A string containing the knownbugregex uri.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """
        url = self.make_url("bugoccurrence")
        data = {
            'testcaseinstance': testcaseinstance_uri,
            'knownbugregex': knownbugregex_uri,
        }
        response = self.make_request('post', url=url, data=json.dumps(data))
        bugoccurrence_uuid = response.json().get('uuid')
        self.LOG.info("Bug Occurrence created (bug occurrence uuid: {})"
                      .format(bugoccurrence_uuid))
        return bugoccurrence_uuid

    # Bug Tracker Bug
    def bugtrackerbug_exists(self, bug_number):
        return self.instance_exists('bugtrackerbug', 'bug_number',
                                    'bug_number', int(bug_number))

    def create_bugtrackerbug(self, bug_number):
        """Creates a new instance of the 'BugTrackerBug' model.

        Args:
            bug_number: A string containing the bug number of the associated
                bug.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        FIXME: This is inconsitent with the other create_* methods in the
        API - we may need to replace this method with one which takes in
        a resource_uri instead of a bug_number.

        """
        url = self.make_url("bugtrackerbug")
        data = {"bug_number": bug_number}
        response = self.make_request('post', url=url, data=json.dumps(data))
        return self.pk_uri('bugtrackerbug', response.json()['uuid'])

    def get_bugtrackerbug_from_bug_number(self, bug_number):
        bugtrackerbug_instances = self.get_instance_data(
            'bugtrackerbug', 'bug_number', 'bug_number', bug_number)
        if bugtrackerbug_instances is not None:
            if bug_number in [str(btbugs.get('bug_number')) for btbugs in
                              bugtrackerbug_instances]:
                return self.pk_uri('bugtrackerbug',
                                    bugtrackerbug_instances[0]['uuid'])

    # Build
    def build_exists(self, build_uuid):
        return self.instance_exists('build', 'uuid', 'uuid', build_uuid)

    def create_build(self, build_id, pipeline, jobtype, testcase_uuid,
                     testcaseinstancestatus, build_started_at=None,
                     build_finished_at=None, ts_format="%Y-%m-%d %H:%M:%SZ"):
        """Creates a new instance of the 'Build' model.

        Please note that all builds will have at least one testcase which
        repesents whether or not the build ran successfully. In these cases,
        the testframework, testcaseclass, and testcase names will be given the
        same name as the jobtype. If the job has multiple sub-tests, there will
        also be one or more appropriately named testframeworks,
        testcaseclasses, and testcases.

        Args:
            build_id: A string containing the build number.
            pipeline: A UUID string used to identify the pipeline.
            jobtype: A string containing the name of the job of which the
                build is an instance.
            testcase_uuid: A UUID string used to identify the testcase.
            testcaseinstancestatus: A string containing the outcome of the
                build.
            build_started_at: A string containing a timestamp representing the
                time the build started.
            build_finished_at: A string containing a timestamp representing
                the time the build ended.
            ts_format: A string containing the start and end timestamps format.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """

        # Create the build:
        url = self.make_url("build")
        data = {
            'build_id': build_id,
            'pipeline': self.pk_uri('pipeline', pipeline),
            'jobtype': self.pk_uri('jobtype', jobtype), }
        if build_started_at is None:
            build_started_at = datetime.now()
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

        # Create testcaseinstance and associate the build:
        self.create_testcaseinstance(
            build_uuid, testcase_uuid, pipeline, testcaseinstancestatus)

        return build_uuid

    def get_build_uuid_from_build_id_job_and_pipeline(self, build_id, jobtype,
                                                      pipeline_uuid):
        build_instances = self.filter_instances(
            "build", {'build_id': build_id, 'jobtype__name': jobtype,
                      'pipeline__uuid': pipeline_uuid}
        )
        if build_instances:
            if build_id in [str(build.get('build_id')) for build in
                            build_instances]:
                return build_instances[0]['uuid']
        msg = "No build with build_id = {} & pipeline_uuid = {}"
        raise UnrecognisedInstance(msg.format(build_id, pipeline_uuid))

    def update_build(self, build_id, pipeline, jobtype, testcase_uuid,
                     testcaseinstancestatus, build_started_at=None,
                     build_finished_at=None, ts_format="%Y-%m-%d %H:%M:%SZ"):
        build_uuid = self.get_build_uuid_from_build_id_job_and_pipeline(
            build_id, jobtype, pipeline)
        url = self.make_url("build", build_uuid)
        data = {
            'pipeline': self.pk_uri('pipeline', pipeline),
            'jobtype': self.pk_uri('jobtype', jobtype),
        }
        if build_started_at:
            data['build_started_at'] =\
                utils.convert_timestamp_to_string(build_started_at, ts_format)
        if build_finished_at is None:
            build_finished_at = datetime.now()
        data['build_finished_at'] =\
            utils.convert_timestamp_to_string(build_finished_at, ts_format)

        response = self.make_request('put', url=url, data=json.dumps(data))
        response_data = response.json()
        build_uuid = response_data['uuid']
        tci_uuid = self.get_testcaseinstance_uuid_from_build_id_testcase_uuid(
            build_id, testcase_uuid)
        self.update_testcaseinstance(tci_uuid, testcaseinstancestatus)
        msg = "Build {} successfully updated (build uuid: {}, status: {})"
        self.LOG.info(msg.format(build_id, build_uuid, testcaseinstancestatus))
        return build_uuid

    # Build Executor
    def get_list_of_buildexecutors(self):
        return [bld_ex['name'] for bld_ex in self.get_objects('buildexecutor')]

    def buildexecutor_exists(self, name):
        buildexecutor_instances = self.filter_instances(
            "buildexecutor",
            {'name': name, 'jenkins__uuid': self._get_jenkins_uuid()})
        return len(buildexecutor_instances) > 0

    def create_buildexecutor(self, buildexecutor_name):
        buildexecutor_name = buildexecutor_name.lstrip('(').rstrip(')')
        jenkins_resource_uri = self.pk_uri(
            'jenkins', self._get_jenkins_uuid())
        url = self.make_url("buildexecutor")
        data = {'name': buildexecutor_name,
                'jenkins': jenkins_resource_uri}
        self.make_request('post', url=url, data=json.dumps(data))

    def get_buildexecutor_uuid_from_name(self, buildexecutor_name):
        objects = self.filter_instances("buildexecutor", {
            'jenkins__uuid': self._get_jenkins_uuid(),
            'name': buildexecutor_name})
        if not objects:
            return
        return objects[0].get('uuid')

    # Environment
    def environment_exists(self, env_uuid):
        return self.instance_exists('environment', 'uuid', 'uuid', env_uuid)

    def create_environment(self, env_name, env_uuid):
        url = self.make_url("environment")
        data = {'name': env_name,
                'uuid': env_uuid}
        response = self.make_request('post', url=url, data=json.dumps(data))
        env_name = response.json()['name']
        self.LOG.info("Set up new {} environment: {}".format(
            env_name, env_uuid))

    def get_env_name_from_uuid(self, uuid):
        url = self.make_url("environment", uuid)
        response = self.make_request('get', url=url)
        return response.json().get('name')

    def get_env_uuid_from_name(self, name):
        objects = self.filter_instances('environment', {'name': name})
        if not objects:
            return
        return objects[0].get('uuid')

    def update_environment(self, uuid, **kwargs):
        url = self.make_url("environment", uuid)
        self.update_instance(url, **kwargs)

    # InternalContact
    def internalcontact_exists(self, name):
        return self.instance_exists('internalcontact', 'name', 'name', name)

    def create_internalcontact(self, name, staffdirectoryurl=None):
        data = {'name': name, }
        if staffdirectoryurl is not None:
            data['staffdirectoryurl'] = staffdirectoryurl
        url = self.make_url("internalcontact")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_internalcontact_from_name(self, name):
        objects = self.filter_instances('internalcontact', {'name': name})
        if not objects:
            return
        return self.pk_uri('internalcontact', objects[0].get('name'))

    # Jenkins
    def jenkins_exists(self, jenkins_uuid):
        return self.instance_exists('jenkins', 'uuid', 'uuid', jenkins_uuid)

    def create_jenkins(self, env_uuid, jenkins_host, default_status='up'):
        url = self.make_url("jenkins")
        data = {
            'environment': self.pk_uri('environment', env_uuid),
            'external_access_url': jenkins_host,
            'internal_access_url': jenkins_host,
            'servicestatus': self.pk_uri('servicestatus', default_status),
        }
        self.make_request('post', url=url, data=json.dumps(data))
        self.LOG.info("Set up new jenkins '{}' for environment {}".format(
            self._get_jenkins_uuid(), env_uuid))

    def _get_jenkins_uuid(self):
        if self._jenkins_uuid is None:
            jenkins = self.get_instance_data(
                'jenkins', 'uuid', 'environment__uuid', self.uuid)
            if len(jenkins) > 0:
                self._jenkins_uuid = jenkins[0]['uuid']
            else:
                self._jenkins_uuid = None
        return self._jenkins_uuid

    def check_in_to_jenkins(self):
        url = self.make_url("jenkins", self._get_jenkins_uuid())
        response = self.make_request('put', url=url, data=json.dumps({}))
        return response.json().get('uuid')

    # Job
    def get_list_of_job_types(self):
        return [job['name'] for job in self.get_objects('jobtype')]

    # JujuService
    def get_list_of_jujuservices(self):
        return [jujuservice['name'] for jujuservice in
                self.get_objects('jujuservice')]

    def jujuservice_exists(self, name):
        return self.instance_exists('jujuservice', 'name', 'name', name)

    def create_jujuservice(self, name):
        """Creates a new instance of the 'JujuService' model.

        Args:
            name: A string containing a summary of the juju service.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """

        url = self.make_url("jujuservice")
        data = {"name": name}
        self.make_request('post', url=url, data=json.dumps(data))

    # JujuServiceDeployment
    def jujuservicedeployment_exists(self, jujuservicedeployment_uuid):
        return self.instance_exists('jujuservicedeployment', 'uuid', 'uuid',
                                    jujuservicedeployment_uuid)

    def create_jujuservicedeployment(self, name, jujuservice_uri=None,
            productundertest=None, unit=None, charm=None):
        """Creates a new instance of the 'jujuservicedeployment' model.

        Args:
            name: A string containing a summary of the juju service deployment.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """

        url = self.make_url("jujuservicedeployment")
        data = {"name": name}
        if jujuservice_uri is not None:
            data['jujuservice'] = jujuservice_uri
        if productundertest is not None:
            data['productundertest'] = productundertest
        if unit is not None:
            data['unit'] = unit
        if charm is not None:
            data['charm'] = charm
        response = self.make_request('post', url=url, data=json.dumps(data))
        response_data = response.json()
        self.LOG.info("jujuservicedeployment (uuid: {}) created successfully."
                      .format(response_data['uuid']))
        return response_data['uuid']

    # KnownBugRegex
    def knownbugregex_exists(self, regex):
        return self.instance_exists('knownbugregex', 'regex', 'regex', regex)

    def create_knownbugregex(self, targetfileglob_list, regex, bug_uri=None):
        url = self.make_url("knownbugregex")
        data = {"targetfileglobs": targetfileglob_list,
                "regex": regex}
        if bug_uri is not None:
            data['bug'] = bug_uri
        self.make_request('post', url=url, data=json.dumps(data))

    def get_knownbugregex_resource_uri_from_regex_uuid(self,
                                                       knownbugregex_uuid):
        return self.pk_uri('knownbugregex', knownbugregex_uuid)

    def get_knownbugregex_from_regex(self, regex):
        knownbugregex_instances = self.get_instance_data(
            'knownbugregex', 'regex', 'regex', regex)
        if knownbugregex_instances is not None:
            if regex in [str(kbregex.get('regex')) for kbregex in
                         knownbugregex_instances]:
                return self.pk_uri(
                    'knownbugregex', knownbugregex_instances[0]['uuid'])

    def get_knownbugregex_target_files(self, regex_resource):
        tfiles = self.get_instances(regex_resource)['targetfileglobs']
        return [urllib.parse.unquote(tfile['glob_pattern']) for tfile in tfiles]

    def update_knownbugregex_with_new_target_file(self, t_file_glob_resource,
                                                  regex_resource):
        tfile_list = self.get_knownbugregex_target_files(regex_resource)
        tfile_list.append(t_file_glob_resource)
        url = self.make_url(regex_resource)
        self.update_instance(url, targetfileglobs=tfile_list)

    # Machine
    def machine_exists(self, uuid):
        return self.instance_exists(
            'machine', 'uuid', 'uuid', uuid)

    def create_machine(self, hostname):
        data = {"hostname": hostname, }
        url = self.make_url("machine")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_machine_from_hostname(self, hostname):
        objects = self.filter_instances("machine", {"hostname": hostname})
        if not objects:
            return
        return self.pk_uri("machine", objects[0].get('uuid'))

    # Machine Configuration
    def machineconfiguration_exists(self, uuid):
        return self.instance_exists(
            'machineconfiguration', 'uuid', 'uuid', uuid)

    def create_machineconfiguration(self, machine=None, pipeline=None,
                                    productundertest_list=None):
        data = {}
        if machine is not None:
            data['machine'] = machine
        if pipeline is not None:
            data['pipeline'] = pipeline
        if productundertest_list is not None:
            data['productundertests'] = productundertest_list
        url = self.make_url("machineconfiguration")
        self.make_request('post', url=url, data=json.dumps(data))

    def update_machineconfiguration(self, uuid, **data):
        url = self.make_url("machineconfiguration", uuid)
        response = self.make_request('put', url=url, data=json.dumps(data))
        return response.json()

    # Openstack Version
    def openstackversion_exists(self, name):
        return self.instance_exists('openstackversion', 'name', 'name', name)

    def create_openstackversion(self, name):
        data = {"name": name, }
        url = self.make_url("openstackversion")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_openstackversion_from_name(self, name):
        return self.pk_uri('openstackversion', name)

    # Pipeline
    def pipeline_exists(self, pipeline_id):
        return self.instance_exists('pipeline', 'uuid', 'uuid', pipeline_id)

    def get_pipeline_uuid_from_env_job_and_build(self, env_uuid, jobtype,
                                                 build_id):
        pipeline_instances = self.filter_instances("pipeline", {
            'builds__build_id': build_id,
            'builds__jobtype__name': jobtype,
            'buildexecutor__jenkins__environment__uuid': env_uuid})
        if pipeline_instances is None:
            return False
        return pipeline_instances[0]['uuid']

    def get_pipeline_from_uuid(self, uuid):
        pipeline_instances = self.get_instance_data(
            'pipeline', 'uuid', 'uuid', uuid)

        if pipeline_instances is not None:
            if uuid in [str(pipeline.get('uuid')) for pipeline in
                        pipeline_instances]:
                return self.pk_uri("pipeline", pipeline_instances[0]['uuid'])

    def update_completed_pipeline(self, pipeline_id, completed_at=None):
        if completed_at is None:
            completed_at = str(datetime.now())
        url = self.make_url("pipeline", pipeline_id)
        data = {'pipeline': pipeline_id,
                'completed_at': completed_at}
        response = self.make_request('put', url=url, data=json.dumps(data))
        return response.json().get('completed_at')

    def update_pipeline(self, pipeline_id, **data):
        url = self.make_url("pipeline", pipeline_id)
        response = self.make_request('put', url=url, data=json.dumps(data))
        return response.json()

    def upload_bundle_image(self, pipeline_id, image):
        url = self.make_url("pipeline", pipeline_id, "bundleimage")
        files = {'bundleimage': open(image, 'rb')}
        # bypass self.make_request and call requests.post directly
        # because self.make_requests doesn't support a multipart file upload
        response = requests.post(url=url, files=files)
        return response.json()

    def get_bundle_image(self, pipeline_id):
        url = self.make_url("pipeline", pipeline_id, "bundleimage")[:-1]
        response = self.make_request('get', url=url)
        return response.content

    # Product Under Test
    def get_list_of_products(self):
        return [product['name'] for product in
                self.get_objects('productundertest')]

    def productundertest_exists(self, name):
        return self.instance_exists('productundertest', 'name', 'name', name)

    def create_productundertest(self, name, project=None, vendor=None,
                                internalcontact=None, producttype=None,
                                report_list=None):
        data = {"name": name, }
        if project is not None:
            data['project'] = project
        if vendor is not None:
            data['vendor'] = vendor
        if internalcontact is not None:
            data['internalcontact'] = internalcontact
        if producttype is not None:
            data['producttype'] = producttype
        if report_list is not None:
            data['reports'] = report_list
        url = self.make_url("productundertest")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_productundertest_from_name(self, name):
        objects = self.filter_instances("productundertest", {'name': name})
        if not objects:
            return
        return self.pk_uri("productundertest", objects[0].get('uuid'))

    # Project
    def get_list_of_projects(self):
        return [project['name'] for project in self.get_objects('project')]

    def project_exists(self, name):
        return self.instance_exists('project', 'name', 'name', name)

    def create_project(self, name):
        data = {"name": name, }
        url = self.make_url("project")
        self.make_request('post', url=url, data=json.dumps(data))

    # Report
    def get_list_of_reports(self):
        return [report['name'] for report in self.get_objects('report')]

    def report_exists(self, uuid):
        return self.instance_exists('report', 'uuid', 'uuid', uuid)

    def create_report(self, name):
        """Creates a new instance of the 'Report' model.

        Args:
            name: A string containing the name of the report.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """

        url = self.make_url("report")
        data = {"name": name}
        self.make_request('post', url=url, data=json.dumps(data))

    # ReportPeriod
    def get_list_of_reportperiods(self):
        return [reportperiod['name'] for reportperiod in
                self.get_objects('reportperiod')]

    def reportperiod_exists(self, uuid):
        return self.instance_exists('reportperiod', 'uuid', 'uuid', uuid)

    def create_reportperiod(self, name):
        """Creates a new instance of the 'ReportPeriod' model.

        Args:
            name: A string containing the name of the report period.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """

        url = self.make_url("reportperiod")
        data = {"name": name}
        self.make_request('post', url=url, data=json.dumps(data))

    # ReportInstance
    def reportinstance_exists(self, uuid):
        return self.instance_exists('reportinstance', 'uuid', 'uuid', uuid)

    def create_reportinstance(self, report=None, reportperiod=None):
        """Creates a new instance of the 'ReportInstance' model.

        Args:
            report: A string containing the resource uri of the report.
            reportperiod: A string containing the resource uri of the
                report period.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """

        url = self.make_url("reportinstance")
        data = {}
        if report is not None:
            data['report'] = report
        if reportperiod is not None:
            data['reportperiod'] = reportperiod
        self.make_request('post', url=url, data=json.dumps(data))

    # Target File Glob
    def targetfileglob_exists(self, glob_pattern):
        return self.instance_exists('targetfileglob', 'glob_pattern',
                                    'glob_pattern', glob_pattern)

    def create_targetfileglob(self, glob_pattern, jobtypes_list=None):
        data = {"glob_pattern": glob_pattern, }

        if jobtypes_list is not None:
            data["jobtypes"] = jobtypes_list

        url = self.make_url("targetfileglob")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_targetfileglob_from_glob(self, targetfileglob):
        targetfileglob_instances = self.get_instance_data(
            'targetfileglob', 'glob_pattern', 'glob_pattern', targetfileglob)

        if targetfileglob_instances is not None:
            if targetfileglob in [str(tfile.get('glob_pattern')) for tfile in
                                  targetfileglob_instances]:
                return self.pk_uri('targetfileglob',
                               targetfileglob_instances[0]['glob_pattern'])

    def get_targetfileglob_jobtypes(self, t_file_glob_resource):
        return self.get_instances(t_file_glob_resource)['jobtypes']

    def update_targetfileglob_with_new_jobtype(self, job_resource,
                                               t_file_glob_resource):
        job_list = self.get_targetfileglob_jobtypes(t_file_glob_resource)
        job_list.append(job_resource)
        url = self.make_url(t_file_glob_resource)
        self.update_instance(url, jobtypes=job_list)

    # TestCase
    def testcase_exists(self, testcase_uuid):
        return self.instance_exists('testcase', 'uuid', 'uuid', testcase_uuid)

    def get_testcase_uuid_from_name_and_testcaseclass_uuid(self, name,
                                                           testcaseclass_uuid):
        testcase_instance = self.filter_instances(
            "testcase",
            {'name': name, 'testcaseclass_uuid': testcaseclass_uuid})
        try:
            return testcase_instance[0]['uuid']
        except IndexError:
            msg = "No testcases found with name: {} and testcaseclass uuid: {}"
            raise UnrecognisedInstance(msg.format(name, testcaseclass_uuid))

    def create_testcase(self, name, testcaseclass_uuid):
        """Creates a new instance of the 'TestCase' model.

        Args:
            name: A string containing the name of the testcaseclass.
            testcaseclass_uuid: A string containing the uuid of the
                testcaseclass.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.
            UnrecognisedInstance: An error will occur if there is not a
                TestFramework that matches the given name and version.

        """

        url = self.make_url("testcase")
        data = {
            'name': name,
            'testcaseclass': self.pk_uri('testcaseclass', testcaseclass_uuid),
        }

        response = self.make_request('post', url=url, data=json.dumps(data))
        response_data = response.json()
        self.LOG.info("The {} TestCase was created successfully.".format(
            response_data['name']))
        return response_data['uuid']

    def get_or_create_testcase(self, name, testcaseclass_uuid):
        """ Try to create testcase """
        try:
            testcase_uuid =\
                self.get_testcase_uuid_from_name_and_testcaseclass_uuid(
                    name=name, testcaseclass_uuid=testcaseclass_uuid)
        except UnrecognisedInstance:
            testcase_uuid = self.create_testcase(
                name=name, testcaseclass_uuid=testcaseclass_uuid)
        self.LOG.info("Testcase '{}', uuid: : {}".format(
            name, testcase_uuid))
        return testcase_uuid

    # TestCaseClass
    def testcaseclass_exists(self, testcaseclass_uuid):
        return self.instance_exists(
            'testcaseclass', 'uuid', 'uuid', testcaseclass_uuid)

    def get_testcaseclass_uuid_from_name_testfw_uuid(self, name,
                                                     testframework_uuid):
        testcaseclass_instance = self.filter_instances(
            "testcaseclass",
            {'name': name, 'testframework__uuid': testframework_uuid})
        try:
            return testcaseclass_instance[0]['uuid']
        except IndexError:
            msg = "No testframeworks found with name: {} and "
            msg += "testframework uuid: {}"
            raise UnrecognisedInstance(msg.format(name, testframework_uuid))

    def create_testcaseclass(self, name, testframework_uuid):
        """Creates a new instance of the 'TestCaseClass' model.

        Args:
            name: A string containing the name of the test framework.
            testframework_uuid: A string containing the uuid of the test
                framework of which this TestCaseClass is a part.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.
            UnrecognisedInstance: An error will occur if there is not a
                TestFramework that matches the given name and version.

        """

        url = self.make_url("testcaseclass")
        data = {
            'name': name,
            'testframework': self.pk_uri('testframework', testframework_uuid),
        }

        response = self.make_request('post', url=url, data=json.dumps(data))
        response_data = response.json()
        self.LOG.info("The {} TestCaseClass was created successfully."
                      .format(response_data['name']))
        return response_data['uuid']

    def get_or_create_testcaseclass(self, name, testframework_uuid):
        """ Try to create testcaseclass """
        try:
            testcaseclass_uuid =\
                self.get_testcaseclass_uuid_from_name_testfw_uuid(
                    name=name, testframework_uuid=testframework_uuid)
        except UnrecognisedInstance:
            testcaseclass_uuid = self.create_testcaseclass(
                name=name, testframework_uuid=testframework_uuid)
        self.LOG.info("TestCaseClass '{}', uuid: : {}".format(
            name, testcaseclass_uuid))
        return testcaseclass_uuid

    # TestCaseInstance
    def testcaseinstance_exists(self, testcaseinstance_uuid):
        return self.instance_exists(
            'testcaseinstance', 'uuid', 'uuid', testcaseinstance_uuid)

    def get_testcaseinstance_uuid_from_build_id_testcase_uuid(self, build_id,
                                                              testcase_uuid):
        testcaseinstance = self.filter_instances(
            "testcaseinstance",
            {'build__build_id': build_id, 'testcase__uuid': testcase_uuid})
        try:
            return testcaseinstance[0]['uuid']
        except IndexError:
            msg = "No testcaseinstance found with build_id: {} and testcase: {}"
            raise UnrecognisedInstance(msg.format(build_id, testcase_uuid))

    def get_or_create_testcaseinstance(self, build_id, build_uuid, testcase_uuid,
                                       pipeline_uuid, testcaseinstancestatus):
        """Tries to create a new instance of the 'TestCase' model
        if one doesn't already exist.

        Args:
            build_id: A string containing the build number.
            build_uuid: A UUID string used to identify the build.
            testcase_uuid: A UUID string used to identify the testcase.
            pipeline_uuid: A UUID string used to identify the pipeline.
            testcaseinstancestatus: A string containing the testcaseinstance
                status.
        """

        try:
            testcaseinstance_uuid =\
                self.get_testcaseinstance_uuid_from_build_id_testcase_uuid(
                    build_id, testcase_uuid)
        except UnrecognisedInstance:
            testcaseinstance_uuid = self.create_testcaseinstance(build_uuid,
                                        testcase_uuid, pipeline_uuid,
                                        testcaseinstancestatus)
        return testcaseinstance_uuid

    def create_testcaseinstance(self, build_uuid, testcase_uuid, pipeline_uuid,
                                testcaseinstancestatus):
        """Creates a new instance of the 'TestCase' model.

        Args:
            build_uuid: A UUID string used to identify the build.
            testcase_uuid: A UUID string used to identify the testcase.
            pipeline_uuid: A UUID string used to identify the pipeline.
            testcaseinstancestatus: A string containing the testcaseinstance
                status.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.
            UnrecognisedInstance: An error will occur if there is not a
                TestFramework that matches the given name and version.

        """

        url = self.make_url("testcaseinstance")
        data = {
            'testcase': self.pk_uri('testcase', testcase_uuid),
            'testcaseinstancestatus': self.pk_uri(
                'testcaseinstancestatus', testcaseinstancestatus),
            'build': self.pk_uri('build', build_uuid),
        }

        response = self.make_request('post', url=url, data=json.dumps(data))
        response_data = response.json()
        self.LOG.info("TestCaseInstance with uuid: {} created successfully."
                      .format(response_data['uuid']))
        return response_data['uuid']

    def update_testcaseinstance(self, testcaseinstance_uuid,
                                testcaseinstancestatus):
        url = self.make_url("testcaseinstance", testcaseinstance_uuid)
        tci_pk = self.pk_uri('testcaseinstancestatus', testcaseinstancestatus)
        data = {'testcaseinstancestatus': tci_pk, }
        response = self.make_request('put', url=url, data=json.dumps(data))
        response_data = response.json()
        return response_data['uuid']

    def get_testcaseinstance_uuid(self, build_id, testcase_name,
                                  testcaseclass_name, testframework_name,
                                  testframework_version):
        testcaseinstance_resource_uri = self.get_testcaseinstance_resource_uri(
            build_id, testcase_name, testcaseclass_name, testframework_name,
            testframework_version)
        return self.get_pk_from_resource_uri(testcaseinstance_resource_uri)

    def get_testcaseinstance_resource_uri(self, build_id, testcase_name,
                                          testcaseclass_name,
                                          testframework_name,
                                          testframework_version):
        testframework_uuid =\
            self.get_testframework_uuid_from_name_and_ver(
                testframework_name, testframework_version)
        testcaseclass_uuid =\
            self.get_testcaseclass_uuid_from_name_testfw_uuid(
                testcaseclass_name, testframework_uuid)
        testcase_uuid =\
            self.get_testcase_uuid_from_name_and_testcaseclass_uuid(
                testcase_name, testcaseclass_uuid)
        testcaseinstance_uuid =\
            self.get_testcaseinstance_uuid_from_build_id_testcase_uuid(
                build_id, testcase_uuid)
        return self.get_testcaseinstance_uri_from_uuid(testcaseinstance_uuid)

    def get_testcaseinstance_uri_from_uuid(self, uuid):
        return self.pk_uri('testcaseinstance', uuid)

    # TestFramework
    def testframework_exists(self, testframework_uuid):
        return self.instance_exists(
            'testframework', 'uuid', 'uuid', testframework_uuid)

    def get_testframework_uuid_from_name_and_ver(self, name, version):
        try:
            testframeworks = self.filter_instances(
                "testframework", {'name': name, 'version': version})
            return testframeworks[0]['uuid']
        except IndexError:
            msg = "No testframeworks found with name: {} and version: {}"
            raise UnrecognisedInstance(msg.format(name, version))

    def create_testframework(self, name, description=None,
                             version='notapplicable'):
        """Creates a new instance of the 'TestFramework' model.

        Args:
            name: A string containing the name of the test framework.
            description: A string describing the test framework.
            version: A string containing the version of the test framework.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """

        url = self.make_url("testframework")
        data = {'name': name,
                'version': version, }
        if description:
            data['description'] = description

        response = self.make_request('post', url=url, data=json.dumps(data))
        response_data = response.json()
        self.LOG.info("The {} TestFramework was created successfully."
                      .format(response_data['name']))
        return response_data['uuid']

    def get_or_create_testframework(self, name, version):
        """ Try to create testframework """
        try:
            testframework_uuid =\
                self.get_testframework_uuid_from_name_and_ver(
                    name=name, version=version)
        except UnrecognisedInstance:
            testframework_uuid = self.create_testframework(
                name=name, version=version)
        self.LOG.info("Testframework '{}', version '{}', uuid: : {}".format(
            name, version, testframework_uuid))
        return testframework_uuid

    # Ubuntu Version
    def ubuntuversion_exists(self, name):
        return self.instance_exists('ubuntuversion', 'name', 'name', name)

    def create_ubuntuversion(self, name):
        data = {"name": name, }
        url = self.make_url("ubuntuversion")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_ubuntuversion_from_name(self, name):
        return self.pk_uri('ubuntuversion', name)

    # Unit
    def unit_exists(self, unit_uuid):
        return self.instance_exists('unit', 'uuid', 'uuid', unit_uuid)

    def create_unit(self, number, machineconfiguration_uri=None,
                    jujuservicedeployment_uri=None):
        """Creates a new instance of the 'Unit' model.

        Args:
            number: A string containing the number of the unit.
            machineconfiguration_uri: A string containing the resource uri of
                the associated machine configuration.
            jujuservicedeployment_uri: A string containing the resource uri of
                the associated juju service deployment.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """

        url = self.make_url("unit")
        data = {"number": number}
        if machineconfiguration_uri is not None:
            data['machineconfiguration'] = machineconfiguration_uri
        if jujuservicedeployment_uri is not None:
            data['jujuservicedeployment'] = jujuservicedeployment_uri
        response = self.make_request('post', url=url, data=json.dumps(data))
        response_data = response.json()
        self.LOG.info("unit (uuid: {}) created successfully."
                      .format(response_data['uuid']))
        return response_data['uuid']

    # Vendor
    def get_list_of_vendors(self):
        return [vendor['name'] for vendor in self.get_objects('vendor')]

    def vendor_exists(self, name):
        return self.instance_exists('vendor', 'name', 'name', name)

    def create_vendor(self, name):
        data = {"name": name, }
        url = self.make_url("vendor")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_vendor_from_name(self, name):
        return self.pk_uri('vendor', name)
