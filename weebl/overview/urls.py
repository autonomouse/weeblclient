from django.conf.urls import patterns, url

from overview import views

uuid_match = "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"

urlpatterns = patterns('',
    url(r'^$', views.main_page, name='main_page'),
    url(r'stats', views.oil_stats, name='oil_stats'),
    url(r'maintenance', views.maintenance_history,
        name='maintenance_history'),
    url(r'tools', views.tools, name='tools'),
    url(r'job/(?P<job>\S+)/$', views.job_specific_bugs_list,
        name='job_specific_bugs_list'),
    url(r'bug/(?P<bug_id>\d+)/$', views.specific_bug_info,
        name='specific_bug_info'),
    url(r'pipelines/(?P<bug_id>\d+)/$', views.bug_specific_pipelines,
        name='bug_specific_pipelines'),
    url(r'event/(?P<event_id>\d+)/$', views.event_specific_details,
        name='event_specific_details'),
    url(r'vendor/(?P<vendor>\S+)/$', views.specific_vendor_info,
        name='specific_vendor_info'),
    url(r'bugs_hit/(?P<pipeline_id>{})/$'.format(uuid_match),
        views.pipeline_specific_bugs, name='specific_bug_info'),
    url(r'charts', views.charts, name='charts'),
    url(r'categories_and_tags', views.categories_and_tags,
        name='categories_and_tags'),
    url(r'bugs_list', views.bugs_list, name='bugs_list'),
    url(r'vendor_and_hardware', views.vendor_and_hardware,
        name='vendor_and_hardware'),
    url(r'oil_control', views.oil_control, name='oil_control'),
    url(r'machine/(?P<machine>\S+)/$', views.specific_machine_history,
        name='specific_machine_history'),
)
