import json
import utils
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from tastypie import http
from tastypie import exceptions
from tastypie.bundle import Bundle
from django.conf.urls import url
from oilserver.common import StatusChecker
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
