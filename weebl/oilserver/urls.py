from django.conf.urls import patterns, url
from oilserver import views


urlpatterns = patterns('',
                       url(r'^$', views.main_page, name='main_page'),
                       url(r'job/(?P<job>\S+)/$',
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),
                       )
