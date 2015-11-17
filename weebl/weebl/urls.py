from django.conf.urls import patterns, include, url
from tastypie.api import Api
from oilserver.api import resources
from weebl.__init__ import __api_version__
from django.contrib import admin


v_api = Api(api_name=__api_version__)
v_api.register(resources.EnvironmentResource())
v_api.register(resources.ServiceStatusResource())
v_api.register(resources.JenkinsResource())
v_api.register(resources.BuildExecutorResource())
v_api.register(resources.PipelineResource())
v_api.register(resources.BuildStatusResource())
v_api.register(resources.JobTypeResource())
v_api.register(resources.BuildResource())
v_api.register(resources.TargetFileGlobResource())
v_api.register(resources.KnownBugRegexResource())
v_api.register(resources.BugResource())
v_api.register(resources.BugTrackerBugResource())
v_api.register(resources.BugOccurrenceResource())
v_api.register(resources.UbuntuVersionResource())
v_api.register(resources.OpenstackVersionResource())
v_api.register(resources.SDNResource())
v_api.register(resources.ComputeResource())
v_api.register(resources.BlockStorageResource())
v_api.register(resources.ImageStorageResource())
v_api.register(resources.DatabaseResource())
v_api.register(resources.ProjectResource())

urlpatterns = patterns(
    '',
    url(r'^', include('oilserver.urls')),
    url(r'^api/', include(v_api.urls)),
    url(r'api/', include('tastypie_swagger.urls',
                         namespace='api_docs'),
                         kwargs={"tastypie_api_module": "weebl.urls.v_api",
                                 "namespace": "api_docs",
                                 "version": __api_version__}),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
    )
