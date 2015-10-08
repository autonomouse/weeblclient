from django.conf.urls import patterns, url
from oilserver import views
import utils


urlpatterns = patterns('', url(r'^$', views.main_page, name='index'), )
