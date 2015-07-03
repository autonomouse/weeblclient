from django.conf.urls import patterns, include, url
from tastypie.api import Api
from oilserver.api.resources import (
    EnvironmentResource, 
    ServiceStatusResource,
    JenkinsResource
    )

v_api = Api(api_name='v1')
v_api.register(EnvironmentResource())
v_api.register(ServiceStatusResource())
v_api.register(JenkinsResource())

urlpatterns = patterns('',
                       url(r'^', include('oilserver.urls')),
                       url(r'^api/', include(v_api.urls)),
                       )
