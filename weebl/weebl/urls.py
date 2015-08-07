from django.conf.urls import patterns, include, url
from tastypie.api import Api
from oilserver.api import resources
from weebl.__init__ import __api_version__


v_api = Api(api_name=__api_version__)
v_api.register(resources.EnvironmentResource())
v_api.register(resources.ServiceStatusResource())
v_api.register(resources.JenkinsResource())
v_api.register(resources.BuildExecutorResource())
v_api.register(resources.PipelineResource())
v_api.register(resources.BuildStatusResource())
v_api.register(resources.JobTypeResource())
v_api.register(resources.BuildResource())

urlpatterns = patterns('',
                       url(r'^', include('oilserver.urls')),
                       url(r'^api/', include(v_api.urls)),
                       url(r'api/',
                           include('tastypie_swagger.urls',
                                   namespace='api_docs'),
                           kwargs={"tastypie_api_module": "weebl.urls.v_api",
                                   "namespace": "api_docs",
                                   "version": __api_version__}),)
