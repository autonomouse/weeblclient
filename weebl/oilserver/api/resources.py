import os
import utils
from tastypie import fields
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from django.conf.urls import url
from oilserver import models
from tastypie.exceptions import BadRequest


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


class EnvironmentResource(CommonResource):

    class Meta:
        queryset = models.Environment.objects.all()
        list_allowed_methods = ['get', 'post', 'put', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'name']
        authorization = Authorization()
        always_return_data = True

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
        end_point = "by_name"
        name_regex = "(?P<name>\w[\w/-]*)"
        resource_regex = "P<resource_name>{})".format(self._meta.resource_name)
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
        list_allowed_methods = ['get', 'post', 'put', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True

    def hydrate(self, bundle):
        # Update timestamp (also prevents user submitting timestamp data):
        bundle.data['service_status_updated_at'] = utils.time_now()
        return bundle

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
        list_allowed_methods = ['get', 'post', 'put', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True
        filtering = {'jenkins': ALL_WITH_RELATIONS,
                     'name': ALL_WITH_RELATIONS, }

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

    def hydrate(self, bundle):
        fields_to_remove = ['uuid', 'pk']
        # Hide database structure details by obscuring the primary key.
        # Also, the UUID field is read-only, so don't allow user to change it.
        bundle.data = utils.pop(bundle.data, fields_to_remove)
        return bundle


class PipelineResource(CommonResource):
    build_executor = fields.ForeignKey(BuildExecutorResource, 'build_executor')

    class Meta:
        queryset = models.Pipeline.objects.all()
        fields = ['uuid', 'build_executor']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'delete']  # individual
        authorization = Authorization()
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj.build_executor = models.BuildExecutor.objects.get(
            uuid=bundle.data['build_executor'])
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

    def hydrate(self, bundle):
        fields_to_remove = ['uuid', 'pk']
        # Hide database structure details by obscuring the primary key.
        # Also, the UUID field is read-only, so don't allow user to change it.
        bundle.data = utils.pop(bundle.data, fields_to_remove)
        return bundle


class BuildStatusResource(CommonResource):

    class Meta:
        resource_name = 'build_status'
        queryset = models.BuildStatus.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        fields = ['name', 'description']
        authorization = Authorization()
        always_return_data = True

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

    def dehydrate(self, bundle):
        replace_with = [('resource_uri', bundle.obj.name), ]
        return self.replace_bundle_item_with_alternative(bundle, replace_with)


class BuildResource(CommonResource):
    pipeline = fields.ForeignKey(PipelineResource, 'pipeline')
    build_status = fields.ForeignKey(BuildStatusResource, 'build_status')
    job_type = fields.ForeignKey(JobTypeResource, 'job_type')

    class Meta:
        queryset = models.Build.objects.all()
        list_allowed_methods = ['get', 'post', 'put', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'build_id', 'artifact_location', 'build_started_at',
                  'build_finished_at', 'build_analysed_at', 'pipeline',
                  'build_status', 'job_type']
        authorization = Authorization()
        always_return_data = True

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
        fields_to_remove = ['uuid', 'pk', 'build_analysed_at']
        bundle.data = utils.pop(bundle.data, fields_to_remove)
        return bundle
