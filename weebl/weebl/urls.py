from django.conf.urls import patterns, include, url
from tastypie.api import Api
from oilserver.api import resources

v_api = Api(api_name='v1')
v_api.register(resources.EnvironmentResource())
v_api.register(resources.ServiceStatusResource())
v_api.register(resources.JenkinsResource())

urlpatterns = patterns('',
                       url(r'^', include('oilserver.urls')),
                       url(r'^api/', include(v_api.urls)),
                       )
