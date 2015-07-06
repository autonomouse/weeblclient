from django.conf.urls import patterns, url
from oilserver import views


end = '$'
catch_all = r'^'
job_path = r'job/(?P<job>\S+)/'
time_range = r'(?P<time_range>\S+)/'
specific_env = r'(?P<specific_env>\S+)/'
weekly = r'weekly/'


urlpatterns = patterns('',
                       url(catch_all + end,
                           views.main_page,
                           name='main_page'),
                       )
