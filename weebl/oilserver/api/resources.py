import json
import utils
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from tastypie import http
from tastypie import exceptions
from django.conf.urls import url
from oilserver.models import (
    WeeblSetting,
    Environment,
    ServiceStatus,
    Jenkins
    )


class EnvironmentResource(ModelResource):
    class Meta:
        queryset = Environment.objects.all()
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
            actual_primary_key = Environment.objects.get(uuid=uuid).pk
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
        if Environment.objects.filter(name=name).exists():
            environment = Environment.objects.get(name=name)
        bundle = self.build_bundle(obj=environment, request=request)
        return self.create_response(request, self.full_dehydrate(bundle))

class ServiceStatusResource(ModelResource):
    class Meta:
        resource_name = 'service_status'
        queryset = ServiceStatus.objects.all()
        list_allowed_methods = ['get']
        fields = ['name', 'description']
        authorization = Authorization()
        always_return_data=True


class JenkinsResource(ModelResource):
    class Meta:
        environment = fields.ForeignKey(EnvironmentResource, 'environment')
        service_status =\
            fields.ForeignKey(ServiceStatusResource, 'service_status')
        
        queryset = Jenkins.objects.all()
        excludes = ['service_status_updated_at']
        fields = ['environment', 'service_status', 'external_access_url',
                  'internal_access_url', 'service_status_updated_at']
        authorization = Authorization()
        always_return_data=True
        

    
    def obj_create(self, bundle, request=None, **kwargs):
        #if 'uuid' not in bundle.data:
        #    import pdb; pdb.set_trace()
        #    return self.create_response(request, bundle, 
        #                                response_class = http.HttpForbidden)
        try:
            bundle.obj.external_access_url = bundle.data['external_access_url']
            #if 'internal_access_url' in bundle.data:
            #    bundle.obj.internal_access_url =\
            #        bundle.data['internal_access_url']
            #else:
            #    bundle.obj.internal_access_url = ''
            #import pdb; pdb.set_trace()
        except:
            pass
        bundle.obj.save()
        return bundle
    

    def dehydrate(self, bundle):
        status_checker = StatusChecker()
        environment = Environment.objects.get(uuid=bundle.data['uuid'])
        
        
        status_checker.get_current_oil_state(environment)
        
        ##import pdb; pdb.set_trace()
        #bundle.data['status'] = 'test'
        #bundle.data['status_description'] = 'test'
        
        #environment.status = 'this'
        #environment.status_description = 
        
        '''
        Environment.objects.get(uuid=bundle.data['uuid']).pk
        update_output = environment.update_status(**request_dict)
        return self.create_response(request, update_output)
        '''
        return bundle



