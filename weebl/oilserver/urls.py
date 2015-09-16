from django.conf.urls import patterns, url
from oilserver import views
import utils

end = '$'
catch_all = r'^'
job_path = r'job/(?P<job>\S+)/'
time_range = r'(?P<time_range>\S+)/'
specific_env = r'(?P<specific_env>\S+)/'
uuid = r'(?P<uuid>{})/'.format(utils.uuid_re_pattern())
weekly = r'weekly/'


urlpatterns = patterns('',
                       url(catch_all + end,
                           views.main_page,
                           name='index'),

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

                       url("^environment/" + uuid + end,
                           views.environment_page,
                           name='environment_page'),
                       )
