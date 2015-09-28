import os
import utils
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from django.conf.urls import url
from oilserver import models
from tastypie.exceptions import BadRequest
from exceptions import NonUserEditableError


class CommonResource(ModelResource):

    def replace_bundle_item_with_alternative(self, bundle, replace_with):
        if replace_with is None:
            return bundle
        for replace_this, with_this in replace_with:
            if type(bundle.data[replace_this]) is int:
                replace_me = bundle.data[replace_this]
            else:
                replace_me =\
                    os.path.dirname(bundle.data[replace_this].rstrip('/'))
            bundle.data[replace_this] = "{}/{}/".format(replace_me, with_this)
        return bundle

    def raise_error_if_in_bundle(self, bundle, error_if_fields):
        bad_fields = []
        for field in error_if_fields:
            if field in bundle.data:
                bad_fields.append(field)
        if bad_fields:
            msg = "Cannot edit field(s): {}".format(", ".join(bad_fields))
            raise NonUserEditableError(msg)

    def specify_many_to_many_fields(self, resource_name, model, field, bundle):
        resources = bundle.data.get(resource_name, [])
        resource_list = [resources] if type(resources) != list else resources
        output = []
        for resource in resource_list:
            output.append(self.get_or_create_if_doesnt_exist(
                          resource, model, field, bundle))
        return output

    def get_or_create_if_doesnt_exist(self, resource, model, field, bundle):
        field_filter = {field: resource}
        if not model.objects.filter(**field_filter).exists():
            # Create target file if doesn't exist:
            instance = model()
            setattr(instance, field, resource)
            instance.save()
        return model.objects.get(**field_filter)

    def hydrate(self, bundle):
        # Timestamp data should be generated interanlly and not editable:
        error_if_fields = ['created_at', 'updated_at']
        self.raise_error_if_in_bundle(bundle, error_if_fields)

        # Hide database structure details by obscuring the primary key, also,
        # the UUID field is read-only, so don't allow user to change it:
        fields_to_remove = ['uuid', 'pk']
        bundle.data = utils.pop(bundle.data, fields_to_remove)
        return bundle


class EnvironmentResource(CommonResource):

    class Meta:
        queryset = models.Environment.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL, }

    def obj_create(self, bundle, request=None, **kwargs):
        # Update name if one is supplied:
        if 'name' in bundle.data:
            bundle.obj.name = bundle.data['name']
        if 'uuid' in bundle.data:
            bundle.obj.uuid = bundle.data['uuid']
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk."""
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # Because end-point is the UUID not pk really
            actual_primary_key = models.Environment.objects.get(uuid=uuid).pk
            kwargs['pk'] = actual_primary_key
            kwargs['uuid'] = uuid
        return super(EnvironmentResource, self).dispatch(request_type, request,
                                                         **kwargs)

    def prepend_urls(self):
        # Create "by_name" as a new end-point:
        resource_regex = "P<resource_name>{})".format(self._meta.resource_name)
        name_regex = "(?P<name>\w[\w/-]*)"
        end_point = "by_name"
        new_url = r"^(?{}/{}/{}{}$".format(resource_regex, end_point,
                                           name_regex, trailing_slash())
        return [url(new_url,
                    self.wrap_view('get_by_name'),
                    name="api_get_by_name"), ]

    def get_by_name(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        name = kwargs['name']
        if models.Environment.objects.filter(name=name).exists():
            environment = models.Environment.objects.get(name=name)
            bundle = self.build_bundle(obj=environment, request=request)
            return self.create_response(request, self.full_dehydrate(bundle))

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.uuid), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)

    def hydrate(self, bundle):
        # Don't use CommonResource's hydrate method for Environment.
        return bundle


class ServiceStatusResource(CommonResource):

    class Meta:
        resource_name = 'service_status'
        queryset = models.ServiceStatus.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        fields = ['name', 'description']
        authorization = Authorization()
        always_return_data = True

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.name), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class JenkinsResource(CommonResource):
    environment = fields.ForeignKey(EnvironmentResource, 'environment')
    service_status = fields.ForeignKey(ServiceStatusResource, 'service_status')

    class Meta:
        queryset = models.Jenkins.objects.all()
        fields = ['environment', 'service_status', 'external_access_url',
                  'internal_access_url', 'service_status_updated_at']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL, }

    def hydrate(self, bundle):
        # Update timestamp (also prevents user submitting timestamp data):
        bundle.data['service_status_updated_at'] = utils.time_now()
        return super(JenkinsResource, self).hydrate(bundle)

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj.environment = models.Environment.objects.get(
            uuid=bundle.data['environment'])
        bundle.obj.service_status =\
            models.ServiceStatus.objects.get(name='unknown')

        if 'external_access_url' in bundle.data:
            bundle.obj.external_access_url = bundle.data['external_access_url']
        else:
            bundle.obj.external_access_url = bundle.data['external_access_url']

        if 'internal_access_url' in bundle.data:
            bundle.obj.internal_access_url = bundle.data[
                'jenkins_internal_url']
        else:
            bundle.obj.internal_access_url = bundle.data[
                'external_access_url']

        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk."""
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # Because end-point is the UUID not pk really
            # Match the UUID to an Environment instance and work out the pk of
            # this Jenkins instance from that:
            if models.Environment.objects.filter(uuid=uuid).exists():
                env = models.Environment.objects.get(uuid=uuid)
                kwargs['pk'] = env.jenkins.pk
                kwargs['environment'] = env
                # TODO: else return and error code
        return super(JenkinsResource, self).dispatch(request_type, request,
                                                     **kwargs)

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.environment.uuid),
                        ('environment', bundle.obj.environment.uuid),
                        ('service_status', bundle.obj.service_status.name), ]
        bundle.data['uuid'] = bundle.obj.uuid
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class BuildExecutorResource(CommonResource):
    jenkins = fields.ForeignKey(JenkinsResource, 'jenkins')

    class Meta:
        resource_name = 'build_executor'
        queryset = models.BuildExecutor.objects.all()
        fields = ['name', 'uuid', 'jenkins']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True
        filtering = {'jenkins': ALL_WITH_RELATIONS,
                     'name': ALL,
                     'uuid': ALL, }

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj.jenkins =\
            models.Environment.objects.get(uuid=bundle.data['jenkins']).jenkins

        if 'name' in bundle.data:
            bundle.obj.name = bundle.data['name']
        else:
            bundle.obj.name = bundle.obj.uuid
        bundle.obj.save()
        return bundle

    def obj_get_list(self, bundle, **kwargs):
        """This overrides the default obj_get_list method with an extra block
        of code to replace the jenkins uuid given with the respective pk, so
        the user can simply pass in a uuid rather than having to know the
        primary keys for this table in the database (which is also potentially
        insecure).
        """
        filters = {}

        if hasattr(bundle.request, 'GET'):
            # Grab a mutable copy.
            filters = bundle.request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)

        # Replace uuid with pk so can filter by env/jenkins uuid instead of pk:
        if 'jenkins' in filters:
            jenkins_uuid = filters['jenkins'].rstrip('/').split('/')[-1]
            env_pk = models.Environment.objects.get(uuid=jenkins_uuid).pk
            jenkins_pk = models.Jenkins.objects.get(environment_id=env_pk).pk
            filters['jenkins'] = str(jenkins_pk)

        applicable_filters = self.build_filters(filters=filters)

        try:
            objects = self.apply_filters(bundle.request, applicable_filters)
            return self.authorized_read_list(objects, bundle)
        except ValueError:
            msg = "Invalid resource lookup data provided (mismatched type)."
            raise BadRequest(msg)

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk."""
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # Because end-point is the UUID not pk really
            if models.BuildExecutor.objects.filter(uuid=uuid).exists():
                build_executor = models.BuildExecutor.objects.get(uuid=uuid)
                kwargs['pk'] = build_executor.pk
                # TODO: else return and error code
        return super(BuildExecutorResource, self).dispatch(
            request_type, request, **kwargs)

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.uuid),
                        ('jenkins', bundle.obj.jenkins.uuid), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class UbuntuVersionResource(CommonResource):

    class Meta:
        resource_name = 'ubuntu_version'
        queryset = models.UbuntuVersion.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'number']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }

    def obj_create(self, bundle, request=None, **kwargs):
        if 'name' in bundle.data:
            bundle.obj.name = bundle.data['name']
        if 'number' in bundle.data:
            bundle.obj.number = bundle.data['number']
        bundle.obj.save()
        return bundle

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.name), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class OpenstackVersionResource(CommonResource):

    class Meta:
        resource_name = 'openstack_version'
        queryset = models.OpenstackVersion.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }

    def obj_create(self, bundle, request=None, **kwargs):
        if 'name' in bundle.data:
            bundle.obj.name = bundle.data['name']
        bundle.obj.save()
        return bundle

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.name), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class SDNResource(CommonResource):

    class Meta:
        resource_name = 'sdn'
        queryset = models.SDN.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }

    def obj_create(self, bundle, request=None, **kwargs):
        if 'name' in bundle.data:
            bundle.obj.name = bundle.data['name']
        bundle.obj.save()
        return bundle

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.name), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class PipelineResource(CommonResource):
    build_executor = fields.ForeignKey(BuildExecutorResource, 'build_executor')
    ubuntu_version = fields.ForeignKey(UbuntuVersionResource, 'ubuntu_version',
                                       full=True, null=True)
    openstack_version = fields.ForeignKey(
        OpenstackVersionResource, 'openstack_version', full=True, null=True)
    sdn = fields.ForeignKey(SDNResource, 'sdn', full=True, null=True)

    class Meta:
        queryset = models.Pipeline.objects.all()
        fields = ['uuid', 'build_executor', 'completed_at', 'ubuntu_version', 
                  'openstack_version', 'sdn']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'completed_at': ALL,
                     'ubuntu_version': ALL_WITH_RELATIONS,
                     'openstack_version': ALL_WITH_RELATIONS,
                     'sdn': ALL_WITH_RELATIONS}

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj.build_executor = models.BuildExecutor.objects.get(
            uuid=bundle.data['build_executor'])
        if 'completed_at' in bundle.data:
            bundle.obj.completed_at = bundle.data['completed_at']
        else:
            bundle.obj.completed_at = None
        if 'pipeline' in bundle.data:
            bundle.obj.uuid = bundle.data['pipeline']

        if 'ubuntu_version' in bundle.data:
            bundle.obj.ubuntu_version = self.get_or_create_if_doesnt_exist(
                bundle.data['ubuntu_version'], models.UbuntuVersion,
                'name', bundle)
        if 'openstack_version' in bundle.data:
            bundle.obj.openstack_version = self.get_or_create_if_doesnt_exist(
                bundle.data['openstack_version'], models.OpenstackVersion,
                'name', bundle)
        if 'sdn' in bundle.data:
            bundle.obj.sdn = self.get_or_create_if_doesnt_exist(
                bundle.data['sdn'], models.SDN, 'name', bundle)
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk."""
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # Because end-point is the UUID not pk really
            if models.Pipeline.objects.filter(uuid=uuid).exists():
                pipeline = models.Pipeline.objects.get(uuid=uuid)
                kwargs['pk'] = pipeline.pk
                # TODO: else return and error code
        return super(PipelineResource, self).dispatch(request_type, request,
                                                      **kwargs)

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.uuid),
                        ('build_executor', bundle.obj.build_executor.uuid), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class BuildStatusResource(CommonResource):

    class Meta:
        resource_name = 'build_status'
        queryset = models.BuildStatus.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        fields = ['name', 'description']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.name), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class JobTypeResource(CommonResource):

    class Meta:
        resource_name = 'job_type'
        queryset = models.JobType.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        fields = ['name', 'description']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.name), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class BuildResource(CommonResource):
    pipeline = fields.ForeignKey(PipelineResource, 'pipeline')
    build_status = fields.ForeignKey(BuildStatusResource, 'build_status')
    job_type = fields.ForeignKey(JobTypeResource, 'job_type')

    class Meta:
        queryset = models.Build.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'build_id', 'artifact_location', 'build_started_at',
                  'build_finished_at', 'build_analysed_at', 'pipeline',
                  'build_status', 'job_type']
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'build_id': ALL,
                     'job_type': ALL_WITH_RELATIONS,
                     'pipeline': ALL_WITH_RELATIONS,
                     'build_status': ALL_WITH_RELATIONS}

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj.build_id = bundle.data['build_id']
        bundle.obj.pipeline = models.Pipeline.objects.get(
            uuid=bundle.data['pipeline'])
        bundle.obj.build_status = models.BuildStatus.objects.get(
            name=bundle.data['build_status'])
        bundle.obj.job_type = models.JobType.objects.get(
            name=bundle.data['job_type'])
        if 'build_started_at' in bundle.data:
            bundle.obj.build_started_at = bundle.data['build_started_at']
        if 'build_finished_at' in bundle.data:
            bundle.obj.build_finished_at = bundle.data['build_finished_at']
        bundle.obj.build_analysed_at = utils.time_now()
        # Link to Jenkins, but in the future, consider changing this to S3:
        jenkins_ext_url =\
            bundle.obj.pipeline.build_executor.jenkins.external_access_url
        url = "{}/job/{}/{}/artifact/artifacts/"
        bundle.obj.artifact_location = url.format(
            jenkins_ext_url, bundle.data['job_type'], bundle.data['build_id'])
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk."""
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # Because end-point is the UUID not pk really
            if models.Build.objects.filter(uuid=uuid).exists():
                build = models.Build.objects.get(uuid=uuid)
                kwargs['pk'] = build.pk
                # TODO: else return and error code
        return super(BuildResource, self).dispatch(request_type, request,
                                                   **kwargs)

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.uuid),
                        ('build_status', bundle.obj.build_status),
                        ('job_type', bundle.obj.job_type),
                        ('pipeline', bundle.obj.pipeline.uuid), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)

    def hydrate(self, bundle):
        fields_to_remove = ['build_analysed_at']
        bundle.data = utils.pop(bundle.data, fields_to_remove)
        return super(BuildResource, self).hydrate(bundle)


class TargetFileGlobResource(CommonResource):

    class Meta:
        resource_name = 'target_file_glob'
        queryset = models.TargetFileGlob.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['glob_pattern', 'job_type']
        authorization = Authorization()
        always_return_data = True
        filtering = {'glob_pattern': ALL, }

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj.glob_pattern = bundle.data['glob_pattern']
        bundle.obj.save()
        bundle.obj.job_types = self.specify_many_to_many_fields(
            "job_types", models.JobType, 'name', bundle)
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk."""
        if 'pk' in kwargs:
            glob_pattern = kwargs['pk']  # As end-point is glob_pattern not pk
            if models.TargetFileGlob.objects.filter(glob_pattern=glob_pattern
                                                    ).exists():
                target_file_glob = models.TargetFileGlob.objects.get(
                    glob_pattern=glob_pattern)
                kwargs['pk'] = target_file_glob.pk
                # TODO: else return and error code
        return super(TargetFileGlobResource, self).dispatch(request_type,
                                                            request, **kwargs)

    def dehydrate(self, bundle):
        if hasattr(bundle.obj, 'job_types'):
            bundle.data['job_types'] = [
                job.name for job in bundle.obj.job_types.all()]
        replace_with = [('resource_uri', bundle.obj.glob_pattern), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)

    def hydrate(self, bundle):
        if 'job_types' in bundle.data:
            bundle.obj.job_types = self.specify_many_to_many_fields(
                "job_types", models.JobType, 'name', bundle)
        return super(TargetFileGlobResource, self).hydrate(bundle)


class KnownBugRegexResource(CommonResource):

    class Meta:
        resource_name = 'known_bug_regex'
        queryset = models.KnownBugRegex.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['bug', 'uuid', 'regex', 'target_file_globs',
                  'created_at', 'updated_at']
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'regex': ALL, }

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj.regex = bundle.data['regex']
        bundle.obj.save()

        if 'bug' in bundle.data:
            bundle.obj.bug = self.get_or_create_if_doesnt_exist(
                bundle.data['bug'], models.Bug, 'uuid', bundle)
        bundle.obj.target_file_globs = self.specify_many_to_many_fields(
            "target_file_globs", models.TargetFileGlob, 'glob_pattern', bundle)
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk."""
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # Because end-point is the UUID not pk really
            if models.KnownBugRegex.objects.filter(uuid=uuid).exists():
                regex = models.KnownBugRegex.objects.get(uuid=uuid)
                kwargs['pk'] = regex.pk
                # TODO: else return and error code
        return super(KnownBugRegexResource, self).dispatch(
            request_type, request, **kwargs)

    def dehydrate(self, bundle):
        bundle.data['bug'] = bundle.obj.bug
        bundle.obj.save()

        if hasattr(bundle.obj, 'target_file_globs'):
            bundle.data['target_file_globs'] = [
                tfglob.glob_pattern for tfglob in
                bundle.obj.target_file_globs.all()]
        replace_with = [('resource_uri', bundle.obj.uuid), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)

    def hydrate(self, bundle):
        if 'target_file_globs' in bundle.data:
            bundle.obj.target_file_globs = self.specify_many_to_many_fields(
                "target_file_globs", models.TargetFileGlob, 'glob_pattern',
                bundle)
        return super(KnownBugRegexResource, self).hydrate(bundle)


class BugResource(CommonResource):

    class Meta:
        queryset = models.Bug.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'summary', 'description', 'bug_tracker_bugs',
                  'created_at', 'updated_at']
        authorization = Authorization()
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        # Update details if supplied:
        bundle.obj.summary = bundle.data['summary']
        bundle.obj.description = bundle.data.get('description')
        bundle.obj.save()
        if 'bug_tracker_bugs' in bundle.data:
            bundle.obj.bug_tracker_bugs = self.specify_many_to_many_fields(
                "bug_tracker_bugs", models.BugTrackerBug, 'bug_id', bundle)
            bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk.
        """
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # As end-point is uuid not pk
            if models.Bug.objects.filter(uuid=uuid).exists():
                bug = models.Bug.objects.get(uuid=uuid)
                kwargs['pk'] = bug.pk
                # TODO: else return and error code
        return super(BugResource, self).dispatch(
            request_type, request, **kwargs)

    def dehydrate(self, bundle):
        if hasattr(bundle.obj, 'bug_tracker_bugs'):
            bundle.data['bug_tracker_bugs'] = [
                usbugs.bug_id for usbugs in bundle.obj.bug_tracker_bugs.all()]
        replace_with = [('resource_uri', bundle.obj.uuid), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)

    def hydrate(self, bundle):
        if 'bug_tracker_bugs' in bundle.data:
            bundle.obj.bug_tracker_bugs = self.specify_many_to_many_fields(
                "bug_tracker_bugs", models.BugTrackerBug, 'bug_id', bundle)
        return super(BugResource, self).hydrate(bundle)


class BugTrackerBugResource(CommonResource):

    class Meta:
        resource_name = 'bug_tracker_bug'
        queryset = models.BugTrackerBug.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'bug_id', 'created_at', 'updated_at']
        authorization = Authorization()
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        # Update details if supplied:
        bundle.obj.bug_id = bundle.data['bug_id']
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk.
        """
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # As end-point is uuid not pk
            if models.BugTrackerBug.objects.filter(uuid=uuid).exists():
                bug_tracker_bug = models.BugTrackerBug.objects.get(uuid=uuid)
                kwargs['pk'] = bug_tracker_bug.pk
                # TODO: else return and error code
        return super(BugTrackerBugResource, self).dispatch(
            request_type, request, **kwargs)

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.bug_id), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class BugOccurrenceResource(CommonResource):
    build = fields.ForeignKey(BuildResource, 'build')
    regex = fields.ForeignKey(KnownBugRegexResource, 'regex')

    class Meta:
        resource_name = 'bug_occurrence'
        queryset = models.BugOccurrence.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'build', 'regex', 'created_at', 'updated_at']
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'build': ALL_WITH_RELATIONS,
                     'regex': ALL_WITH_RELATIONS, }

    def obj_create(self, bundle, request=None, **kwargs):
        if 'build' in bundle.data:
            bundle.obj.build = models.Build.objects.get(
                uuid=bundle.data['build'])
        if 'regex' in bundle.data:
            bundle.obj.regex = models.KnownBugRegex.objects.get(
                uuid=bundle.data['regex'])
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        """Overrides and replaces the the uuid in the end-point with pk."""
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # Because end-point is the UUID not pk really
            if models.BugOccurrence.objects.filter(uuid=uuid).exists():
                bug_occurrence = models.BugOccurrence.objects.get(uuid=uuid)
                kwargs['pk'] = bug_occurrence.pk
                # TODO: else return and error code
        return super(BugOccurrenceResource, self).dispatch(request_type,
                                                           request, **kwargs)

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.uuid), ]
        if bundle.obj.regex is not None:
            replace_with.append(('regex', bundle.obj.regex.uuid))
        if bundle.obj.build is not None:
            replace_with.append(('build', bundle.obj.build.uuid))
        return self.replace_bundle_item_with_alternative(bundle, replace_with)
