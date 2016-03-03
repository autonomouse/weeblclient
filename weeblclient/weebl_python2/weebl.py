import os
import re
import six
import yaml
import json
import fnmatch
import urllib2
import requests
from dateutil import parser
from datetime import datetime
from weeblclient.weebl_python2 import utils
from requests.exceptions import ConnectionError
from weeblclient.weebl_python2.exception import (
    UnexpectedStatusCode,
    InstanceAlreadyExists,
    UnrecognisedInstance,
    UnauthorisedAPIRequest
)
if six.PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin


class Weebl(object):
    """Weebl API wrapper class.

    This class provides a wrapper around the Python2 weeblclient REST API and
    includes helper methods to enable easier interaction with the Weebl server.

    Attributes:
        LOG: An instance of the Logger class.
        env_name: A string that holds the name of the environment (e.g.
            "production" or "staging")
        uuid: A string containing the UUID representing the environment.
        weebl_api_version: A string representing the version of weebl api used
            by this client.
        weebl_url: The url where weebl is hosted.
        headers: A dictionary holding the headers sent along with each API
            request.
        resource_url: A string representing the basis of the resource_uri
            without the initial url part.
        base_url: A string representing the basis of the resource_uri (with
            url).
    """

    def __init__(self, uuid, env_name, username=None, apikey=None,
                 weebl_url="http://10.245.0.14",
                 weebl_api_ver="v1"):
        self.username = username
        self.LOG = utils.get_logger("weeblSDK_python2")
        self.env_name = env_name
        self.uuid = uuid
        self.weebl_api_version = weebl_api_ver
        self.weebl_url = weebl_url
        self.headers = {"content-type": "application/json",
                        "limit": None}
        if username is not None:
            self.headers["Authorization"] =\
                "ApiKey {}:{}".format(username, apikey)
        self.resource_url = "/api/{}/".format(weebl_api_ver)
        self.base_url = urljoin(weebl_url, self.resource_url)
        self._jenkins_uuid = None

    def make_url(self, *path_list, **kwargs):
        query = kwargs.get('query')
        path = "/".join([item.lstrip('/').rstrip('/') for item in path_list])
        if "api/v1/" in path:
            path = path[7:]
        url = urljoin(self.base_url, path) + '/'
        if query is not None:
            return url + query
        return url

    def make_request(self, method, **payload):
        payload['headers'] = self.headers
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
            raise(e)

        # If response code isn't 2xx:
        msg = "{} request to {} returned a status code of {}"
        err_str = 'duplicate key value violates'
        if str(response.status_code) == '401':
            msg = "{} is not authorised to make this {} request to {}.".format(
                self.username, method, payload['url'])
            raise UnauthorisedAPIRequest(msg)
        elif str(response.status_code) == '500' and err_str in response.text:
            obj = payload['url'].rstrip('/').split('/')[-2]
            msg += " - {} already exists."
            raise InstanceAlreadyExists(msg.format(
                method, payload['url'], response.status_code, obj))
        if str(response.status_code)[0] != '2':
            msg += ":\n\n {}\n"
            raise UnexpectedStatusCode(msg.format(method, payload['url'],
                                       response.status_code, response.text))
        return response

    def get_objects(self, obj, params=None, query=None):
        return self.get_instances(
            obj, params=params, query=query).get('objects')

    def get_instances(self, obj, params=None, query=None):
        """Returns a single instance from the url that is made up of the
        base_url and the given 'obj' path, where obj is the part of the url
        that follows the base_url (e.g. base_url is http://www.foo.bar/ and the
        obj is foobar in this url: http://www.foo.bar/foobar/).
        """
        response = self.make_request(
            'get', url=self.make_url(obj, query=query), params=params)
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
        return self.get_objects(obj, query=filter_by)

    def update_instance(self, url, **kwargs):
        response = self.make_request('put', url=url, data=json.dumps(kwargs))

        try:
            return response.json()
        except ValueError:
            return []
        except UnexpectedStatusCode:
            return []

    def _pk_uri(self, resource, value):
        return "/api/%s/%s/%s/" % (
            self.weebl_api_version, resource, value)

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

    def get_bug_info(self, force_refresh=True):
        self.LOG.info("Downloading bug regexs from Weebl: {}"
                      .format(self.weebl_url))
        targetfileglobs = self.get_objects("targetfileglob")
        knownbugregexes = self.get_objects("knownbugregex")
        bugs = self.get_objects("bug")
        return utils.munge_bug_info_data(
            targetfileglobs, knownbugregexes, bugs)

    def upload_bugs_from_bugs_dictionary(self, bugs_dict,
                                         include_generics=False):
        self.LOG.info("Uploading bugs to Weebl @ {}".format(self.weebl_url))
        entry_list = utils.generate_bug_entries(bugs_dict, include_generics)
        for count, entry in enumerate(entry_list):
            if not self.bugtrackerbug_exists(entry.lp_bug_no):
                self.create_bugtrackerbug(entry.lp_bug_no)
            bugtrackerbug_resource =\
                self.get_bugtrackerbug_from_bug_number(entry.lp_bug_no)

            job_resource = self.get_job_from_job_type(entry.job)
            if not self.targetfileglob_exists(entry.targetfileglob):
                self.create_targetfileglob(
                    entry.targetfileglob, [job_resource])
            t_file_glob_resource = self.get_targetfileglob_from_glob(
                entry.targetfileglob)

            if not self.knownbugregex_exists(entry.regex):
                self.create_knownbugregex([t_file_glob_resource], entry.regex)
            regex_resource = self.get_knownbugregex_from_regex(entry.regex)
            tfiles = self.get_knownbugregex_target_files(regex_resource)
            if t_file_glob_resource not in tfiles:
                self.update_knownbugregex_with_new_target_file(
                    t_file_glob_resource, regex_resource)

            jobtypes = self.get_targetfileglob_jobtypes(t_file_glob_resource)
            if job_resource not in jobtypes:
                self.update_targetfileglob_with_new_jobtype(
                    job_resource, t_file_glob_resource)

            if not self.bug_exists(entry.summary):
                self.create_bug(
                    entry.summary, bugtrackerbug_resource, [regex_resource])
            else:
                bug_resource = self.get_bug_from_summary(entry.summary)
                bug_regexes = self.get_bug_regexes(bug_resource)
                if regex_resource not in bug_regexes:
                    self.update_bug_with_new_bug_regexes(
                        regex_resource, bug_resource)
            print("{}. {} - {} ({}: {})".format(
                  count + 1, entry.lp_bug_no, entry.summary, entry.job,
                  entry.targetfileglob))
        print("\n{} bugs uploaded.\n".format(count + 1))

    def clear_target_files_and_jobs_from_knownbugregexes(self):
        for idx, knownbugregex in enumerate(self.get_objects("knownbugregex")):
            count = idx + 1
            self.LOG.info("Regex {} dissassociated from its target files/jobs."
                          .format(count))
            regex_resource = knownbugregex['resource_uri']
            for targetfileglob_resource in knownbugregex['targetfileglobs']:
                # Clear jobs from TargetFleGlob:
                targetfileglob_url = self.make_url(targetfileglob_resource)
                self.update_instance(targetfileglob_url, jobtypes=[])
            # Clear target files from KnownBugRegex:
            regex_url = self.make_url(regex_resource)
            self.update_instance(regex_url, targetfileglobs=[])
        self.LOG.info("All {} KnownBugRegexes dissassociated.".format(count))

    def import_data_from_doberman_output_folder(self,
                                                doberman_dir,
                                                unformatted_timestamp=None):
        try:
            all_build_exctrs = self.get_list_of_buildexecutors()
            default_build_exctr = ('master' if 'master' in all_build_exctrs
                                   else all_build_exctrs[0])
        except IndexError:
            raise Exception(
                "There are no buildexecutors yet! Please add some.")

        if unformatted_timestamp is None:
            timestamp = self.get_date_from_pipelines_processed(doberman_dir)
        self.create_pipelines_and_builds_from_paabn(
            doberman_dir, timestamp, default_build_exctr)
        self.process_pabb_file(doberman_dir, default_build_exctr)
        self.create_bugs_and_bugoccurrences_from_triage_files(
            doberman_dir, default_build_exctr)

    def get_date_from_pipelines_processed(self, doberman_dir):
        pp_file = os.path.join(doberman_dir, 'pipelines_processed.yaml')
        if not os.path.exists(pp_file):
            return
        with open(pp_file, 'r') as f:
            pp_text = f.read()
        return parser.parse(pp_text.split('\n')[1])

    def create_pipelines_and_builds_from_paabn(self, doberman_dir, timestamp,
                                               build_executor_name):
        print("Loading from %s" % (doberman_dir))
        paabn_file = os.path.join(
            doberman_dir, 'pipelines_and_associated_build_numbers.yml')
        if not os.path.exists(paabn_file):
            return
        with open(paabn_file, 'r') as f:
            paabn = yaml.load(f.read())

        for pipeline, builds in paabn.items():
            try:
                self.create_pipeline(
                    buildexecutor_name=build_executor_name,
                    pipeline_id=pipeline)
            except InstanceAlreadyExists:
                pass

            for job_name, build_id in builds.items():
                if build_id is not None:
                    # Assume build_status was 'success' for now; Update later:
                    try:
                        if timestamp is not None:
                            self.create_build(
                                build_id, pipeline, job_name, 'success',
                                build_finished_at=timestamp)
                        else:
                            self.create_build(
                                build_id, pipeline, job_name, 'success')
                    except InstanceAlreadyExists:
                        pass

    def process_pabb_file(self, doberman_dir, build_executor_name):
        pabb_file = os.path.join(
            doberman_dir, "pipelines_affected_by_bug.yml")
        if not os.path.exists(pabb_file):
            return
        with open(pabb_file, 'r') as f:
            pabb = yaml.load(f.read())
        for bugtrackerbug, pipelines in pabb.items():
            if 'unfiled' in bugtrackerbug:
                continue
            if bugtrackerbug == 'GenericBug_Ignore':
                continue
            for pipeline in pipelines:
                try:
                    # Get bugtrackerbug:
                    btbugs = self.filter_instances("bug", [
                        ('bugtrackerbug__bug_number', bugtrackerbug)])
                    if len(btbugs) == 0:
                        continue
                    btb_instance = btbugs[0]

                    # Use first regex:
                    regex_resource = btb_instance['knownbugregex'][0]
                    regex_uuid =\
                        regex_resource.split('knownbugregex/')[1].split('/')[0]
                    regex_instance = self.filter_instances("knownbugregex", [
                        ('uuid', regex_uuid)])[0]

                    # Get target file:
                    target_file_resource = regex_instance['targetfileglobs'][0]
                    target_file = (
                        target_file_resource.split('targetfileglob/')[1]
                        .split('/')[0])

                    # Use first job
                    job_instance = self.filter_instances("jobtype", [
                        ('targetfileglob__name', target_file)])[0]

                    # Get build
                    build_instance = self.filter_instances("build", [
                        ('pipeline__uuid', pipeline),
                        ('jobtype__name', job_instance['name'])])[0]

                    # Create bug occurrence
                    try:
                        self.create_bugoccurrence(
                            build_instance['uuid'], regex_uuid)
                    except InstanceAlreadyExists as e:
                        pass
                except Exception as e:
                    self.LOG.error("Error processing pipeline: {} for {}\n{}"
                                   .format(pipeline, bugtrackerbug, e))
                    continue

    def create_bugs_and_bugoccurrences_from_triage_files(self, doberman_dir,
                                                         build_executor_name):
        for job in self.get_list_of_job_types():
            # Auto-triaged_unfiled_bugs file: Only present when has unfileds:
            self.process_autotriage(doberman_dir, job, build_executor_name)

            # Triage file: Only present in newer doberman versions:
            self.process_triage_file(doberman_dir, job, build_executor_name)

    def process_autotriage(self, doberman_dir, job, build_executor_name):
        autotriage_file = os.path.join(
            doberman_dir, "auto-triaged_unfiled_bugs.yml")
        if not os.path.exists(autotriage_file):
            return
        with open(autotriage_file, 'r') as f:
            autotriage = yaml.load(f.read())

        for pipeline, unfiled_bugs in autotriage['pipelines'].items():

            if not self.pipeline_exists(pipeline):
                self.create_buildexecutor(build_executor_name)
                self.create_pipeline(
                    buildexecutor_name=build_executor_name,
                    pipeline_id=pipeline)
            processed = []
            for unfiled_bug, details in unfiled_bugs.items():
                build_id = details['build']
                job_name = details['job']
                build_status = details['status'].lower()
                group = (build_id, job_name, build_status)
                if group not in processed:
                    tstamp = datetime.strptime(
                        details['Crude-Analysis timestamp'].split('.')[0],
                        '%Y-%b-%d %H:%M:%S')
                    self.update_build(build_id, pipeline, job_name,
                                      build_status, build_finished_at=tstamp)
                    processed.append(group)

                #
                target_file = details['additional info'].get('target file')
                if target_file is None:
                    continue
                regex_uuid = self.apply_all_regexes_to_text(
                    details['match text'], target_file)
                if regex_uuid is None:
                    continue

                for dup_pipeline in details['duplicates']:
                    if self.pipeline_exists(dup_pipeline):
                        build_instances = self.filter_instances(
                            "build", [('pipeline__uuid', dup_pipeline)])
                        for build in build_instances:
                            build_uuid = self.build_exists(
                                build['build_id'], dup_pipeline)
                            self.create_bugoccurrence(build_uuid, regex_uuid)

    def process_triage_file(self, doberman_dir, job, build_executor_name):
        triage_file = os.path.join(
            doberman_dir, "triage_{}.yml".format(job))
        if not os.path.exists(triage_file):
            return
        with open(triage_file, 'r') as f:
            triage = yaml.load(f.read())

        for pipeline, trg in triage['pipeline'].items():
            self.LOG.info("Processing {} for {} job.".format(
                pipeline, job))
            self.create_pipeline(
                buildexecutor_name=build_executor_name,
                pipeline_id=pipeline)
            build_status = trg['status']
            build_id = trg['build']
            self.create_service_status(build_status)
            job_resource = self.create_jobtype(job)
            build_uuid = self.create_build(
                build_id, pipeline, job, build_status)
            for lp_bug_no, details in trg['bugs'].items():
                not_generic = 'GenericBug_Ignore' not in lp_bug_no
                not_unfiled = 'unfiled' not in lp_bug_no
                if not_generic and not_unfiled:
                    bugtrackerbug = self.create_bugtrackerbug(lp_bug_no)
                    for targetfileglob, regexs in details['regexps'].items():
                        self.create_targetfileglob(
                            targetfileglob, job_resource)
                        re = regexs['regexp'][0]
                        t_file_glob_resource = self._pk_uri(
                            'targetfileglob', targetfileglob)
                        regex_resource = self.create_knownbugregex(
                            t_file_glob_resource, re)
                        summary = re  # Just use regex as summary for now...
                        self.create_bug(
                            summary, bugtrackerbug, regex_resource)
                        regex_uuid = (regex_resource.split('knownbugregex/')
                                      [1].split('/')[0])
                        self.create_bugoccurrence(build_uuid, regex_uuid)

    def apply_all_regexes_to_text(self, text, target_file):
        knownbugregex_instances = self.get_instances("knownbugregex")

        for knownbugregex in knownbugregex_instances:
            regex = knownbugregex['regex']
            regex_uuid = knownbugregex['uuid']
            targetfileglobs = [
                tf.split('/api/v1/targetfileglob/')[1][:-1] for tf in
                knownbugregex['targetfileglobs']]
            matching_tfiles = [glob for glob in targetfileglobs if
                               fnmatch(target_file, glob)]
            if len(matching_tfiles) <= 0:
                return
            matches = re.compile(regex, re.DOTALL).findall(text)
            if len(matches) > 0:
                print('match!!! ' + regex)

                msg = "Unfiled bug matched to {}:\n{}"
                self.LOG.info(msg.format(regex_uuid, regex))
                return regex_uuid
                return

    # Model CRUD Operations (In Alphabetical Order):
    # Block Storage
    def blockstorage_exists(self, name):
        return self.instance_exists('blockstorage', 'name', 'name', name)

    def create_blockstorage(self, name):
        """Creates a new instance of the 'BlockStorage' model.

        Args:
            name: A string containing the name of the block storage.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        """
        data = {"name": name, }
        url = self.make_url("blockstorage")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_blockstorage_from_name(self, name):
        return self._pk_uri('blockstorage', name)

    # Bug
    def bug_exists(self, summary):
        return self.instance_exists('bug', 'summary', 'summary', summary)

    def create_bug(self, summary, bugtrackerbug=None, knownbugregex_list=None):
        """Creates a new instance of the 'Bug' model.

        Args:
            summary: A string containing a summary of the bug.
            bugtrackerbug: A string containing the resource uri of the
                associated bug tracker bug.
            knownbugregex_list: A list of strings containing the resource uris
                for each associated known bug regex.

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

        if knownbugregex_list is not None:
            data['knownbugregex'] = knownbugregex_list
        self.make_request('post', url=url, data=json.dumps(data))

    def get_bug_from_summary(self, summary):
        bug_instances = self.get_instance_data(
            'bug', 'summary', 'summary', summary)
        if bug_instances is not None:
            if summary in [str(bug.get('summary')) for bug in bug_instances]:
                return bug_instances[0]['resource_uri']

    def get_bug_regexes(self, bug_resource):
        return self.get_instances(bug_resource)['knownbugregex']

    def update_bug_with_new_bug_regexes(self, regex_resource, bug_resource):
        regex_list = self.get_bug_regexes(bug_resource)
        regex_list.append(regex_resource)
        url = self.make_url(bug_resource)
        self.update_instance(url, knownbugregex=regex_list)

    # Bug Occurrence
    def bugoccurrence_exists(self, build_uuid, regex_uuid):
        bugoccurrence_instances = self.filter_instances(
            "bugoccurrence", [('build__uuid', build_uuid),
                              ('regex__uuid', regex_uuid)])
        return len(bugoccurrence_instances) > 0

    def create_bugoccurrence(self, build_uuid, regex_uuid):
        """Creates a new instance of the 'BugOccurrence' model.

        Args:
            build_uuid: A string containing the UUID of the associated build.
            regex_uuid: A string containing the UUID of the associated known
                bug regex.

        Raises:
            ConnectionError: An error will occur if the client cannot connect
                to weebl.

        FIXME: This is inconsitent with other create_* methods in the
        API - we may need to replace this method with one which takes in
        resource_uris instead of UUIDs, or maybe have both and rename this as
        create_bugoccurrence_uuids or something..?

        """
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
        return response.json()['resource_uri']

    def get_bugtrackerbug_from_bug_number(self, bug_number):
        bugtrackerbug_instances = self.get_instance_data(
            'bugtrackerbug', 'bug_number', 'bug_number', bug_number)
        if bugtrackerbug_instances is not None:
            if bug_number in [str(btbugs.get('bug_number')) for btbugs in
                              bugtrackerbug_instances]:
                return bugtrackerbug_instances[0]['resource_uri']

    # Build
    def build_exists(self, build_uuid):
        return self.instance_exists('build', 'uuid', 'uuid', build_uuid)

    def create_build(self, build_id, pipeline, jobtype, buildstatus,
                     build_started_at=None, build_finished_at=None,
                     ts_format="%Y-%m-%d %H:%M:%SZ"):
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

    def update_build(self, build_id, pipeline, jobtype, buildstatus,
                     build_started_at=None, build_finished_at=None,
                     ts_format="%Y-%m-%d %H:%M:%SZ"):
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

    # Build Executor
    def get_list_of_buildexecutors(self):
        return [bld_ex['name'] for bld_ex in self.get_objects('buildexecutor')]

    def buildexecutor_exists(self, name):
        buildexecutor_instances = self.filter_instances(
            "buildexecutor", [
                ('name', name),
                ('jenkins__uuid', self._get_jenkins_uuid()),
            ]
        )
        return len(buildexecutor_instances) > 0

    def create_buildexecutor(self, buildexecutor_name):
        buildexecutor_name = buildexecutor_name.lstrip('(').rstrip(')')
        jenkins_resource_uri = self._pk_uri(
            'jenkins', self._get_jenkins_uuid())
        url = self.make_url("buildexecutor")
        data = {'name': buildexecutor_name,
                'jenkins': jenkins_resource_uri}
        self.make_request('post', url=url, data=json.dumps(data))

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

    # Compute Version
    def compute_exists(self, name):
        return self.instance_exists('compute', 'name', 'name', name)

    def create_compute(self, name):
        data = {"name": name, }
        url = self.make_url("compute")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_compute_from_name(self, name):
        return self._pk_uri('compute', name)

    # Database Version
    def database_exists(self, name):
        return self.instance_exists('database', 'name', 'name', name)

    def create_database(self, name):
        data = {"name": name, }
        url = self.make_url("database")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_database_from_name(self, name):
        return self._pk_uri('database', name)

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
        url = self.make_url("environment", "by_name", name)
        response = self.make_request('get', url=url)
        return response.json().get('uuid')

    def update_environment(self, uuid, **kwargs):
        url = self.make_url("environment", uuid)
        self.update_instance(url, **kwargs)

    # Image Storage Version
    def imagestorage_exists(self, name):
        return self.instance_exists('imagestorage', 'name', 'name', name)

    def create_imagestorage(self, name):
        data = {"name": name, }
        url = self.make_url("imagestorage")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_imagestorage_from_name(self, name):
        return self._pk_uri('imagestorage', name)

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
        return self._pk_uri('internalcontact', name)

    # Jenkins
    def jenkins_exists(self, jenkins_uuid):
        return self.instance_exists('jenkins', 'uuid', 'uuid', jenkins_uuid)

    def create_jenkins(self, env_uuid, jenkins_host, default_status='up'):
        url = self.make_url("jenkins")
        data = {
            'environment': self._pk_uri('environment', env_uuid),
            'external_access_url': jenkins_host,
            'internal_access_url': jenkins_host,
            'servicestatus': self._pk_uri('servicestatus', default_status),
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

    def check_in_to_jenkins(self, ci_server_api):
        url = self.make_url("jenkins", self._get_jenkins_uuid())
        response = self.make_request('put', url=url, data=json.dumps({}))
        return response.json().get('uuid')

    # Job
    def get_list_of_job_types(self):
        return [job['name'] for job in self.get_objects('jobtype')]

    def get_job_from_job_type(self, job_type):
        url = self.make_url("jobtype", job_type)
        response = self.make_request('get', url=url)
        return response.json()['resource_uri']

    # KnownBugRegex
    def knownbugregex_exists(self, regex):
        return self.instance_exists('knownbugregex', 'regex', 'regex', regex)

    def create_knownbugregex(self, glob_patterns_list, regex):
        url = self.make_url("knownbugregex")
        data = {"targetfileglobs": glob_patterns_list,
                "regex": regex}
        self.make_request('post', url=url, data=json.dumps(data))

    def get_knownbugregex_from_regex(self, regex):
        knownbugregex_instances = self.get_instance_data(
            'knownbugregex', 'regex', 'regex', regex)
        if knownbugregex_instances is not None:
            if regex in [str(kbregex.get('regex')) for kbregex in
                         knownbugregex_instances]:
                return knownbugregex_instances[0]['resource_uri']

    def get_knownbugregex_target_files(self, regex_resource):
        tfiles = self.get_instances(regex_resource)['targetfileglobs']
        return [urllib2.unquote(tfile['glob_pattern']) for tfile in tfiles]

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
        url = self.make_url("machine")
        url_with_args = "{}?hostname={}".format(url, hostname)
        response = self.make_request('get', url=url_with_args)
        objects = response.json()['objects']
        if objects == []:
            return
        else:
            return self._pk_uri("machine", objects[0].get('uuid'))

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
            data['productundertest'] = productundertest_list
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
        return self._pk_uri('openstackversion', name)

    # Pipeline
    def pipeline_exists(self, pipeline_id):
        return self.instance_exists('pipeline', 'uuid', 'uuid', pipeline_id)

    def create_pipeline(self,
                        buildexecutor_name,
                        pipeline_id=None,
                        ubuntuversion=None,
                        openstackversion=None,
                        sdn=None,
                        compute=None,
                        blockstorage=None,
                        imagestorage=None,
                        database=None):
        """Creates a new instance of the 'Pipeline' model.

        Args:
            buildexecutor_name: A required string representing the name of the
                BuildExecutor.
            pipeline_id: An optional UUID string used to identify the pipeline
                may be provided. This will otherwise be auto-generated.
            ubuntuversion: An optional string used to identify the version of
                ubuntu used.
            openstackversion: An optional string used to identify the version
                of openstack used.
            sdn: An optional string used to identify the sdn used.
            compute: An optional string used to identify the compute used.
            blockstorage: An optional string used to identify the blockstorage
                used.
            imagestorage: An optional string used to identify the imagestorage
                used.
            database: An optional string used to identify the database used.

        Returns:
            A string representing the pipeline (this should be the same as the
                one given for pipeline_id).

        Raises:
            Exception: An error will occur if the pipeline given and the
                pipeline returned do not match.

        """
        # Get Build Executor:
        buildexecutor = self.get_buildexecutor_uuid_from_name(
            buildexecutor_name)

        if buildexecutor is None:
            msg = "Cannot create pipeline - unknown build executor: '{}'"
            self.LOG.error(msg.format(buildexecutor_name))
            raise UnrecognisedInstance(msg.format(buildexecutor_name))

        # Create pipeline:
        url = self.make_url("pipeline")
        data = {'buildexecutor': self._pk_uri('buildexecutor', buildexecutor)}
        if pipeline_id is not None:
            data['uuid'] = pipeline_id
        if ubuntuversion is not None:
            data['ubuntuversion'] = ubuntuversion
        if openstackversion is not None:
            data['openstackversion'] = openstackversion
        if sdn is not None:
            data['sdn'] = sdn
        if compute is not None:
            data['compute'] = compute
        if blockstorage is not None:
            data['blockstorage'] = blockstorage
        if imagestorage is not None:
            data['imagestorage'] = imagestorage
        if database is not None:
            data['database'] = database

        response = self.make_request('post', url=url, data=json.dumps(data))
        returned_pipeline = response.json().get('uuid')
        return returned_pipeline

    def get_pipeline_from_uuid(self, uuid):
        pipeline_instances = self.get_instance_data(
            'pipeline', 'uuid', 'uuid', uuid)

        if pipeline_instances is not None:
            if uuid in [str(pipeline.get('uuid')) for pipeline in
                        pipeline_instances]:
                return pipeline_instances[0]['resource_uri']

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
                                internalcontact=None):
        data = {"name": name, }
        if project is not None:
            data['project'] = project
        if vendor is not None:
            data['vendor'] = vendor
        if internalcontact is not None:
            data['internalcontact'] = internalcontact
        url = self.make_url("productundertest")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_productundertest_from_name(self, name):
        url = self.make_url("productundertest")
        url_with_args = "{}?name={}".format(url, name)
        response = self.make_request('get', url=url_with_args)
        objects = response.json()['objects']
        if objects == []:
            return
        else:
            return self._pk_uri("productundertest", objects[0].get('uuid'))

    # SDN Version
    def sdn_exists(self, name):
        return self.instance_exists('sdn', 'name', 'name', name)

    def create_sdn(self, name):
        data = {"name": name, }
        url = self.make_url("sdn")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_sdn_from_name(self, name):
        return self._pk_uri('sdn', name)

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
                return urllib2.unquote(
                    targetfileglob_instances[0]['resource_uri'])

    def get_targetfileglob_jobtypes(self, t_file_glob_resource):
        return self.get_instances(t_file_glob_resource)['jobtypes']

    def update_targetfileglob_with_new_jobtype(self, job_resource,
                                               t_file_glob_resource):
        job_list = self.get_targetfileglob_jobtypes(t_file_glob_resource)
        job_list.append(job_resource)
        url = self.make_url(t_file_glob_resource)
        self.update_instance(url, jobtypes=job_list)

    # Ubuntu Version
    def ubuntuversion_exists(self, name):
        return self.instance_exists('ubuntuversion', 'name', 'name', name)

    def create_ubuntuversion(self, name):
        data = {"name": name, }
        url = self.make_url("ubuntuversion")
        self.make_request('post', url=url, data=json.dumps(data))

    def get_ubuntuversion_from_name(self, name):
        return self._pk_uri('ubuntuversion', name)

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
        return self._pk_uri('vendor', name)

    def get_job_history(self, environment_uuid, start_date=None):
        params = {
            'uuid': environment_uuid,
            'include_job_history': True,
        }
        if start_date is not None:
            params['history_start_date'] = start_date

        [environment] = self.get_objects('environment', params=params)
        return environment['job_history']
