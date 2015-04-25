from django.conf.urls import patterns, url
from oilserver import views


urlpatterns = patterns('',
                       url(r'^$', views.main_page, name='main_page'),
                       url(r'job/(?P<job>\S+)/(?P<time_range>\S+)/(?P<specific_env>\S+)/$',
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),
                       url(r'job/(?P<job>\S+)/(?P<time_range>\S+)/$',
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),                       
                       url(r'job/(?P<job>\S+)/$',
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),
                       url(r'job/(?P<job>\S+)/weekly/$',
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),
                       url(r'weekly/$',
                           views.weekly_main_page,
                           name='weekly_main_page'),
                       )
