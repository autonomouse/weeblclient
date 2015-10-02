import utils
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from django.conf.urls import url
from oilserver import models
from exceptions import NonUserEditableError


def fixup_set_filters(model_names, applicable_filters):
    """Hack to fix tastypie filter strings.

    Tastypie tries to make filter strings like 'bugoccurrences_set'
    instead of 'bugoccurences'. This replaces the former with the latter
    for a set of model names.

    TODO: see if this can be fixed by specifying reverse relation names
    on models.
    """
    for model_name in model_names:
        bad_keys = []
        set_name = model_name + "_set"
        for key in applicable_filters.keys():
            if set_name in key:
                bad_keys.append(key)
        for bad_key in bad_keys:
            value = applicable_filters.pop(bad_key)
            new_key = bad_key.replace(set_name, model_name)
            applicable_filters[new_key] = value


def raise_error_if_in_bundle(bundle, error_if_fields):
    bad_fields = []
    for field in error_if_fields:
        if field in bundle.data:
            bad_fields.append(field)
    if bad_fields:
        msg = "Cannot edit field(s): {}".format(", ".join(bad_fields))
        raise NonUserEditableError(msg)


class CommonResource(ModelResource):

    def hydrate(self, bundle):
        # Timestamp data should be generated interanlly and not editable:
        error_if_fields = ['created_at', 'updated_at']
        raise_error_if_in_bundle(bundle, error_if_fields)
        return bundle

    def alter_list_data_to_serialize(self, request, data):
        if request.GET.get('meta_only'):
            return {'meta': data['meta']}
        return data

    def get_bundle_detail_data(self, bundle):
        # FIXME: There is apparently a bug in tastypie's ModelResource
        # where PUT doesn't work if this method returns non null. If
        # this isn't used, a new object is created instead of updating
        # the existing one.
        return None


class EnvironmentResource(CommonResource):

    class Meta:
        queryset = models.Environment.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ('exact',)}
        detail_uri_name = 'uuid'

    def prepend_urls(self):
        # Create "by_name" as a new end-point:
        # FIXME: We should use filtering here, not a separate new URL.
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


class ServiceStatusResource(CommonResource):

    class Meta:
        resource_name = 'service_status'
        queryset = models.ServiceStatus.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        fields = ['name', 'description']
        authorization = Authorization()
        always_return_data = True
        detail_uri_name = 'name'


class JenkinsResource(CommonResource):
    environment = fields.ForeignKey(EnvironmentResource, 'environment')
    service_status = fields.ForeignKey(ServiceStatusResource, 'service_status')

    class Meta:
        queryset = models.Jenkins.objects.all()
        fields = ['environment', 'service_status', 'external_access_url',
                  'internal_access_url', 'service_status_updated_at', 'uuid']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'environment': ALL_WITH_RELATIONS,
            'uuid': ('exact',),
        }
        detail_uri_name = 'uuid'

    def hydrate(self, bundle):
        # Update timestamp (also prevents user submitting timestamp data):
        # FIXME: No need for this field now that we have updated_at from
        # the base model.
        bundle.data['service_status_updated_at'] = utils.time_now()
        return super(JenkinsResource, self).hydrate(bundle)


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
        detail_uri_name = 'uuid'


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
        detail_uri_name = 'name'


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
        detail_uri_name = 'name'


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
        detail_uri_name = 'name'


class ComputeResource(CommonResource):

    class Meta:
        resource_name = 'compute'
        queryset = models.Compute.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class BlockStorageResource(CommonResource):

    class Meta:
        resource_name = 'block_storage'
        queryset = models.BlockStorage.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class ImageStorageResource(CommonResource):

    class Meta:
        resource_name = 'image_storage'
        queryset = models.ImageStorage.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class DatabaseResource(CommonResource):

    class Meta:
        resource_name = 'database'
        queryset = models.Database.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class PipelineResource(CommonResource):
    build_executor = fields.ForeignKey(BuildExecutorResource, 'build_executor')
    ubuntu_version = fields.ForeignKey(UbuntuVersionResource, 'ubuntu_version',
                                       full=True, null=True)
    openstack_version = fields.ForeignKey(
        OpenstackVersionResource, 'openstack_version', full=True, null=True)
    sdn = fields.ForeignKey(SDNResource, 'sdn', full=True, null=True)
    compute = fields.ForeignKey(ComputeResource, 'compute',
                                full=True, null=True)
    block_storage = fields.ForeignKey(BlockStorageResource, 'block_storage',
                                      full=True, null=True)
    image_storage = fields.ForeignKey(ImageStorageResource, 'image_storage',
                                      full=True, null=True)
    database = fields.ForeignKey(DatabaseResource, 'database',
                                 full=True, null=True)

    class Meta:
        queryset = models.Pipeline.objects.all()
        fields = ['uuid', 'build_executor', 'completed_at', 'ubuntu_version',
                  'openstack_version', 'sdn', 'compute', 'block_storage',
                  'image_storage', 'database']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'completed_at': ALL,
                     'ubuntu_version': ALL_WITH_RELATIONS,
                     'openstack_version': ALL_WITH_RELATIONS,
                     'sdn': ALL_WITH_RELATIONS,
                     'compute': ALL_WITH_RELATIONS,
                     'block_storage': ALL_WITH_RELATIONS,
                     'image_storage': ALL_WITH_RELATIONS,
                     'database': ALL_WITH_RELATIONS
                     }
        detail_uri_name = 'uuid'


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
        detail_uri_name = 'name'


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
        detail_uri_name = 'name'


class BuildResource(CommonResource):
    pipeline = fields.ForeignKey(PipelineResource, 'pipeline')
    build_status = fields.ForeignKey(BuildStatusResource, 'build_status')
    job_type = fields.ForeignKey(JobTypeResource, 'job_type')

    class Meta:
        queryset = models.Build.objects.select_related(
            'pipeline', 'job_type', 'build_status').all()
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
        detail_uri_name = 'uuid'


class TargetFileGlobResource(CommonResource):
    job_types = fields.ToManyField(JobTypeResource, 'job_types', null=True)

    class Meta:
        resource_name = 'target_file_glob'
        queryset = models.TargetFileGlob.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['glob_pattern', 'job_types']
        authorization = Authorization()
        always_return_data = True
        filtering = {'glob_pattern': ALL, }
        detail_uri_name = 'glob_pattern'


class ProjectResource(CommonResource):

    class Meta:
        queryset = models.Project.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'bug_tracker']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class BugResource(CommonResource):
    """API Resource for 'Bug' model.

    The bug list now includes the list of bug occurrences for the bug.
    TODO: Perhaps the list of occurrences should only be included
    when explicitly requested with a separate parameter, like
    get_occurrence=True?

    Bugs can be filtered by bug occurrence properties (via
    knownbugregex). This allows filtering based on pipeline properties
    such as completed_at, ubuntu_version, etc, by extension.
    """
    knownbugregex = fields.ToManyField(
        'oilserver.api.resources.KnownBugRegexResource',
        'knownbugregex_set', null=True)

    class Meta:
        queryset = models.Bug.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'summary', 'description', 'created_at', 'updated_at']
        authorization = Authorization()
        always_return_data = True
        filtering = {'knownbugregex': ALL_WITH_RELATIONS}
        detail_uri_name = 'uuid'

    def apply_filters(self, request, applicable_filters):
        fixup_set_filters(
            ['bugoccurrence', 'knownbugregex'], applicable_filters)
        return super(BugResource, self).apply_filters(
            request, applicable_filters).distinct()


class BugTrackerBugResource(CommonResource):
    bug = fields.ForeignKey(BugResource, 'bug', full=True, null=True)
    project = fields.ForeignKey(
        ProjectResource, 'project', full=True, null=True)

    class Meta:
        resource_name = 'bug_tracker_bug'
        queryset = models.BugTrackerBug.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'bug_number', 'bug', 'project', 'created_at', 
                  'updated_at']
        authorization = Authorization()
        always_return_data = True
        filtering = {'bug_number': ALL, }
        detail_uri_name = 'uuid'


class KnownBugRegexResource(CommonResource):
    target_file_globs = fields.ToManyField(
        TargetFileGlobResource, 'target_file_globs')
    bug = fields.ForeignKey(BugResource, 'bug', null=True)
    bug_occurrences = fields.ToManyField(
        'oilserver.api.resources.BugOccurrenceResource',
        'bugoccurrence_set', full=True, null=True)

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
                     'regex': ALL,
                     'target_file_globs': ALL_WITH_RELATIONS,
                     'bug_occurrences': ALL_WITH_RELATIONS}
        detail_uri_name = 'uuid'


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
        detail_uri_name = 'uuid'
