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
        queryset = models.ServiceStatus.objects.all()
        list_allowed_methods = ['get', 'post']  # all items
        detail_allowed_methods = ['get']  # individual
        fields = ['name', 'description']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ('exact',), }
        detail_uri_name = 'name'


class JenkinsResource(CommonResource):
    environment = fields.ForeignKey(EnvironmentResource, 'environment')
    servicestatus = fields.ForeignKey(ServiceStatusResource, 'servicestatus')

    class Meta:
        queryset = models.Jenkins.objects.all()
        fields = ['environment', 'servicestatus', 'external_access_url',
                  'internal_access_url', 'servicestatus_updated_at', 'uuid']
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
        bundle.data['servicestatus_updated_at'] = utils.time_now()
        return super(JenkinsResource, self).hydrate(bundle)


class BuildExecutorResource(CommonResource):
    jenkins = fields.ForeignKey(JenkinsResource, 'jenkins')

    class Meta:
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
        queryset = models.Database.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = Authorization()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class PipelineResource(CommonResource):
    buildexecutor = fields.ForeignKey(BuildExecutorResource, 'buildexecutor')
    ubuntuversion = fields.ForeignKey(UbuntuVersionResource, 'ubuntuversion',
                                      full=True, null=True)
    openstackversion = fields.ForeignKey(
        OpenstackVersionResource, 'openstackversion', full=True, null=True)
    sdn = fields.ForeignKey(SDNResource, 'sdn', full=True, null=True)
    compute = fields.ForeignKey(ComputeResource, 'compute',
                                full=True, null=True)
    blockstorage = fields.ForeignKey(BlockStorageResource, 'blockstorage',
                                     full=True, null=True)
    imagestorage = fields.ForeignKey(ImageStorageResource, 'imagestorage',
                                     full=True, null=True)
    database = fields.ForeignKey(DatabaseResource, 'database',
                                 full=True, null=True)

    class Meta:
        queryset = models.Pipeline.objects.all()
        fields = ['uuid', 'buildexecutor', 'completed_at', 'ubuntuversion',
                  'openstackversion', 'sdn', 'compute', 'blockstorage',
                  'imagestorage', 'database']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'completed_at': ALL,
                     'ubuntuversion': ALL_WITH_RELATIONS,
                     'openstackversion': ALL_WITH_RELATIONS,
                     'sdn': ALL_WITH_RELATIONS,
                     'compute': ALL_WITH_RELATIONS,
                     'blockstorage': ALL_WITH_RELATIONS,
                     'imagestorage': ALL_WITH_RELATIONS,
                     'database': ALL_WITH_RELATIONS
                     }
        detail_uri_name = 'uuid'


class BuildStatusResource(CommonResource):

    class Meta:
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
    buildstatus = fields.ForeignKey(BuildStatusResource, 'buildstatus')
    jobtype = fields.ForeignKey(JobTypeResource, 'jobtype')

    class Meta:
        queryset = models.Build.objects.select_related(
            'pipeline', 'jobtype', 'buildstatus').all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'build_id', 'artifact_location', 'build_started_at',
                  'build_finished_at', 'build_analysed_at', 'pipeline',
                  'buildstatus', 'jobtype']
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'build_id': ALL,
                     'jobtype': ALL_WITH_RELATIONS,
                     'pipeline': ALL_WITH_RELATIONS,
                     'buildstatus': ALL_WITH_RELATIONS}
        detail_uri_name = 'uuid'


class TargetFileGlobResource(CommonResource):
    jobtypes = fields.ToManyField('oilserver.api.resources.JobTypeResource',
                                  'jobtypes', null=True)

    class Meta:
        queryset = models.TargetFileGlob.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['glob_pattern', 'jobtypes']
        authorization = Authorization()
        always_return_data = True
        filtering = {'glob_pattern': ALL,
                     'jobtypes': ALL_WITH_RELATIONS, }
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


REPLACE_PREFIX = 'knownbugregex__bugoccurrences__'


def get_bugoccurrence_filters(bundle):
    query_dict = bundle.request.GET
    bugoccurrence_filters = {}
    for key, value in query_dict.items():
        if not key.startswith(REPLACE_PREFIX):
            continue
        filter_name = key.replace(REPLACE_PREFIX, '')

        if filter_name.endswith('__in'):
            bugoccurrence_filters[filter_name] = \
                bundle.request.GET.getlist(key)
        else:
            bugoccurrence_filters[filter_name] = value
    bugoccurrence_filters['regex__bug__uuid'] = bundle.obj.uuid
    return bugoccurrence_filters


def get_bugoccurrences(bundle):
    """Get the bug occurrences that match a bug's filter.

    When bugs are found by bug occurrence properties, this matches
    bug occurrences that match those properties. So if we filter for
    bugs with occurrences in pipelines that completed in 2015, only
    the bug occurrences that completed in 2015 will be included.
    """
    bugoccurrence_filters = get_bugoccurrence_filters(bundle)
    return models.BugOccurrence.objects.filter(**bugoccurrence_filters)


class BugResource(CommonResource):
    """API Resource for 'Bug' model.

    The bug list now includes the list of bug occurrences for the bug.
    TODO: Perhaps the list of occurrences should only be included
    when explicitly requested with a separate parameter, like
    get_occurrence=True?

    Bugs can be filtered by bug occurrence properties (via
    knownbugregex). This allows filtering based on pipeline properties
    such as completed_at, ubuntuversion, etc, by extension.
    """
    knownbugregex = fields.ToManyField(
        'oilserver.api.resources.KnownBugRegexResource',
        'knownbugregex_set', null=True)
    bugtrackerbug = fields.ToOneField(
        'oilserver.api.resources.BugTrackerBugResource',
        'bugtrackerbug', full=True, null=True)

    class Meta:
        queryset = models.Bug.objects.select_related('bugtrackerbug').all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'summary', 'description', 'knownbugregex',
                  'bugtrackerbug', 'created_at', 'updated_at']
        authorization = Authorization()
        always_return_data = True
        filtering = {'summary': ('contains'),
                     'knownbugregex': ALL_WITH_RELATIONS,
                     'bugtrackerbug': ALL_WITH_RELATIONS, }
        detail_uri_name = 'uuid'

    def apply_filters(self, request, applicable_filters):
        fixup_set_filters(
            ['bugoccurrence', 'knownbugregex'], applicable_filters)
        return super(BugResource, self).apply_filters(
            request, applicable_filters).distinct()

    def dehydrate(self, bundle):
        bundle = super(BugResource, self).dehydrate(bundle)
        bugoccurrences = get_bugoccurrences(bundle)
        bundle.data['occurrence_count'] = bugoccurrences.count()
        if bugoccurrences.exists():
            bundle.data['last_seen'] = bugoccurrences.latest(
                'build__pipeline__completed_at').build.pipeline.completed_at
        return bundle


class BugTrackerBugResource(CommonResource):
    project = fields.ForeignKey(
        ProjectResource, 'project', full=True, null=True)

    class Meta:
        queryset = models.BugTrackerBug.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'bug_number', 'project', 'created_at', 'updated_at']
        authorization = Authorization()
        always_return_data = True
        filtering = {'bug_number': ALL, }
        detail_uri_name = 'uuid'


class KnownBugRegexResource(CommonResource):
    targetfileglobs = fields.ToManyField(
        TargetFileGlobResource, 'targetfileglobs')
    bug = fields.ForeignKey(BugResource, 'bug', null=True)
    bugoccurrences = fields.ToManyField(
        'oilserver.api.resources.BugOccurrenceResource',
        'bugoccurrence_set', full=True, null=True)

    class Meta:
        queryset = models.KnownBugRegex.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['bug', 'uuid', 'regex', 'targetfileglobs',
                  'created_at', 'updated_at']
        authorization = Authorization()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'regex': ALL,
                     'targetfileglobs': ALL_WITH_RELATIONS,
                     'bugoccurrences': ALL_WITH_RELATIONS}
        detail_uri_name = 'uuid'


class BugOccurrenceResource(CommonResource):
    build = fields.ForeignKey(BuildResource, 'build')
    regex = fields.ForeignKey(KnownBugRegexResource, 'regex')

    class Meta:
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
