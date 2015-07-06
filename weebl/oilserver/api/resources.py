import os
import json
import utils
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from tastypie import http
from tastypie import exceptions
from django.conf.urls import url
from oilserver import models


class CommonResource(ModelResource):

    def replace_pk_with_alternative(self, bundle, alternative=None):
        if alternative is not None:
            uri = os.path.dirname(bundle.data['resource_uri'].rstrip('/'))
            bundle.data['resource_uri'] = "{}/{}/".format(uri, alternative)
        return bundle

class EnvironmentResource(CommonResource):

    class Meta:
        queryset = models.Environment.objects.all()
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        fields = ['uuid', 'name']
        authorization = Authorization()
        always_return_data=True

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle.obj.name = bundle.data['name']
        except:
            pass
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        ''' Overrides and replaces the the uuid in the end-point with pk. '''
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
        uuid = bundle.data['uuid']
        return self.replace_pk_with_alternative(bundle, uuid)


class ServiceStatusResource(CommonResource):

    class Meta:
        resource_name = 'service_status'
        queryset = models.ServiceStatus.objects.all()
        list_allowed_methods = ['get']
        fields = ['name', 'description']
        authorization = Authorization()
        always_return_data=True

    def dehydrate(self, bundle):
        uuid = bundle.data['uuid']
        return self.replace_pk_with_alternative(bundle, uuid)


class JenkinsResource(CommonResource):
    environment = fields.ForeignKey(EnvironmentResource, 'environment')
    service_status = fields.ForeignKey(ServiceStatusResource, 'service_status')

    class Meta:
        queryset = models.Jenkins.objects.all()
        fields = ['environment', 'service_status', 'external_access_url',
                  'internal_access_url', 'service_status_updated_at']
        authorization = Authorization()
        always_return_data=True

    def hydrate(self, bundle):
        # Update tiemstamp (also prevents user submitting timestamp data):
        bundle.data['service_status_updated_at'] = utils.time_now()
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj.environment =\
            models.Environment.objects.get(name=bundle.data['environment'])
        bundle.obj.service_status =\
            models.ServiceStatus.objects.get(name='unknown')
        bundle.obj.external_access_url = bundle.data['external_access_url']
        if 'jenkins_internal_url' in bundle.data:
            int_url = bundle.data['jenkins_internal_url']
        else:
            int_url = bundle.data['external_access_url']
        bundle.obj.internal_access_url = int_url
        bundle.obj.save()
        return bundle

    def dispatch(self, request_type, request, **kwargs):
        ''' Overrides and replaces the the uuid in the end-point with pk. '''
        if 'pk' in kwargs:
            uuid = kwargs['pk']  # Because end-point is the UUID not pk really
            # Match the UUID to an Environment instance and work out the pk of
            # this Jenkins instance from that:
            env = models.Environment.objects.get(uuid=uuid)
            kwargs['pk'] = env.jenkins.pk
            kwargs['environment'] = env
        return super(JenkinsResource, self).dispatch(request_type, request,
                                                     **kwargs)

    def dehydrate(self, bundle):
        uuid = bundle.obj.environment.uuid
        return self.replace_pk_with_alternative(bundle, uuid)

