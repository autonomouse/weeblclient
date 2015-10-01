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


urlpatterns = patterns('', url(r'^$', views.main_page, name='index'), )
