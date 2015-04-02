from django.conf.urls import patterns, url
from oilserver import views


uuid_match = "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
urlpatterns = patterns('',
                       url(r'^$', views.main_page, name='main_page'),
                       url(r'job/(?P<job>\S+)/$',
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),
                       )
