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

                       url("Settings/" + end,
                           views.settings_page,
                           name='settings_page'),

                       url(job_path + time_range + specific_env + end,
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),

                       url(job_path + time_range + end,
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),

                       url(job_path + end,
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),

                       url(job_path + weekly + end,
                           views.job_specific_bugs_list,
                           name='job_specific_bugs_list'),

                       url(weekly + end,
                           views.weekly_main_page,
                           name='weekly_main_page'),
                       )
