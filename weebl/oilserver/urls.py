from django.conf.urls import patterns, url
from oilserver import views


urlpatterns = patterns('',
                       url(r'^$', views.main_page, name='index'),
                       url(r'^logout/$', views.logout_view),
                       )
